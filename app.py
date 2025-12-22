from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
import requests
import base64
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from translator_fixed import translate
from soltrans import generate_farmer_response
from retriever import retrieve
from crop_preference import prefer_crop_specific
from llm_validator import validate_answers, generate_fallback_answer
from canonicalizer import canonicalize

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


app = Flask(__name__, static_folder='agri-advisor/dist', static_url_path='')
CORS(app)


@app.route("/detect-language", methods=["POST"])
def detect_text_language():
    """
    Detect the language of the input text.
    Uses langdetect library for accurate detection.
    """
    try:
        text = request.json.get("text", "")
        if not text or len(text.strip()) < 3:
            return jsonify({"error": "Text too short for language detection"}), 400
        
        lang_result = detect_language(text)
        
        print(f"[DETECT] Text: '{text[:50]}...' -> {lang_result['name']}")
        
        return jsonify({
            "success": True,
            "language_code": lang_result["code"],
            "language_name": lang_result["name"],
            "confidence": lang_result.get("confidence", True)
        }), 200
        
    except Exception as e:
        print(f"[DETECT] Error: {str(e)}")
        return jsonify({"error": f"Language detection failed: {str(e)}"}), 500


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Transcribe audio from user's microphone.
    For now, we'll return a simpler response and rely on browser's Web Speech API
    or accept text directly from frontend.
    """
    try:
        # Get audio file from request
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        print(f"[TRANSCRIBE] Received audio file, size: {len(audio_data)} bytes")
        
        # For now, return a temporary response
        # The audio file has been received successfully
        # Actual transcription would require Whisper API or similar
        
        return jsonify({
            "success": False,
            "error": "Audio transcription requires API setup. Please use the browser's microphone.",
            "transcribed_text": "",
            "language_code": "en",
            "language_name": "English"
        }), 400
        
    except Exception as e:
        print(f"[TRANSCRIBE] Error: {str(e)}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route("/ask", methods=["POST"])
def ask():
    user_input = (
        request.json.get("query", "")
        if request.is_json
        else request.form.get("query", "")
    )
    
    # Get optional language info from frontend (from transcription)
    frontend_language = (
        request.json.get("language", "")
        if request.is_json
        else request.form.get("language", "")
    )

    print("[USER]", user_input)
    if frontend_language:
        print(f"[LANGUAGE] User specified: {frontend_language}")

    # 1. Translate to English using translator_fixed
    translated = translate(user_input)
    print("[ENGLISH TRANSLATION]", translated)
    
    # 2. Detect crop using simple keyword matching
    crop = None
    crop_keywords = ["tomato", "rice", "paddy", "wheat", "corn", "potato", "onion", "chili", "pepper", "cotton", "lemon", "coriander", "cabbage", "spinach", "gourd"]
    for keyword in crop_keywords:
        if keyword.lower() in translated.lower():
            crop = keyword
            break

    # Use canonicalizer to reformat query to match dataset style
    try:
        canonical_q = canonicalize(translated)
        print("[CANONICAL]", canonical_q)
    except Exception as e:
        print(f"[CANONICALIZER ERROR] {e}, using translated query as fallback")
        canonical_q = translated

    # Retrieve with multi-answer support - Get top 10
    candidates = retrieve(canonical_q, top_k=10)  # Get top 10 matched questions

    # Crop-specific preference (for best match display)
    best = prefer_crop_specific(candidates, crop) if candidates else None

    # Collect ALL answers from ALL candidates to get top 10 answers total
    # Prioritize non-placeholder answers
    all_candidate_answers = []
    placeholder_answers = []
    
    if candidates:
        for candidate in candidates:
            for ans in candidate.get("answers", []):
                answer_data = {
                    "text": ans["text"],
                    "confidence": float(ans["confidence"]),  # Ensure float
                    "rank": ans.get("rank", 1),
                    "is_placeholder": ans.get("is_placeholder", False)
                }
                
                # Separate placeholders from real answers
                if ans.get("is_placeholder", False):
                    placeholder_answers.append(answer_data)
                else:
                    all_candidate_answers.append(answer_data)
        
        # Sort real answers by confidence (highest first)
        all_candidate_answers.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Only add placeholders if we don't have enough real answers
        if len(all_candidate_answers) < 10:
            placeholder_answers.sort(key=lambda x: x["confidence"], reverse=True)
            # Add placeholders to fill up to 10, but with lower priority
            remaining_slots = 10 - len(all_candidate_answers)
            all_candidate_answers.extend(placeholder_answers[:remaining_slots])
        
        # Take top 10
        all_candidate_answers = all_candidate_answers[:10]
        print(f"[APP] Collected {len(all_candidate_answers)} answers ({len([a for a in all_candidate_answers if not a.get('is_placeholder', False)])} real, {len([a for a in all_candidate_answers if a.get('is_placeholder', False)])} placeholders) from {len(candidates)} candidates")

    if not best or not all_candidate_answers:
        # Generate fallback answers using LLM
        print("[APP] No candidates found, generating fallback answers")
        fallback_answers = generate_fallback_answer(canonical_q, crop, num_answers=10)
        
        answers_formatted = []
        for idx, ans in enumerate(fallback_answers[:10], 1):
            answers_formatted.append({
                "text": ans["text"],
                "confidence": round(float(ans.get("confidence", 0.4)), 4),
                "rank": idx
            })
        
        response = {
            "translated": translated,
            "original_language": "Unknown",
            "canonical": canonical_q,
            "advice": answers_formatted[0]["text"] if answers_formatted else "No advice available",
            "confidence": round(float(answers_formatted[0]["confidence"]), 4) if answers_formatted else 0.3,
            "all_answers": answers_formatted,
            "matched_question": None,
            "answer_count": len(answers_formatted),
            "source_count": 0,
            "disclaimer": "⚠️ This answer was generated using AI as no exact match was found in our database. Please verify with local agricultural experts for critical decisions.",
            "is_validated": False,
            "validation_reason": "No matching data found - generated LLM answers"
        }
        
        # Reformat advice to user's original language if needed
        if response["advice"]:
            try:
                # Use solution_translator to detect language and reformat answer
                result = generate_farmer_response(user_input, response["advice"])
                print(f"[SOLUTION TRANSLATOR] Result: {result}")
                response["original_language_advice"] = result.get("response", response["advice"])
                response["user_language_type"] = result.get("language_type", "unknown")
                response["original_language"] = result.get("language_type", "Unknown")
                print(f"[SOLUTION TRANSLATOR] Detected language: {result.get('language_type', 'unknown')}")
                print(f"[SOLUTION TRANSLATOR] Reformatted: {response['original_language_advice'][:100] if response['original_language_advice'] else 'None'}")
            except Exception as e:
                print(f"[SOLUTION TRANSLATOR ERROR] {e}, keeping English response")
                response["original_language_advice"] = response["advice"]
                response["user_language_type"] = "unknown"
    else:
        # Format top 10 answers from all candidates
        answers_formatted = []
        for idx, ans in enumerate(all_candidate_answers[:10], 1):
            answers_formatted.append({
                "text": ans["text"],
                "confidence": round(float(ans["confidence"]), 4),
                "rank": idx
            })
        
        print(f"[APP] Formatted {len(answers_formatted)} answers for display")
        
        # 6️⃣ Validate answers using LLM
        print(f"[APP] Validating {len(answers_formatted)} answers with LLM...")
        validation = validate_answers(canonical_q, answers_formatted, crop)
        
        # If answers are NOT valid, generate LLM answers instead
        if not validation.get("is_valid", True) or len(validation.get("validated_answers", [])) == 0:
            # Answers are irrelevant/wrong - Generate LLM answers
            print("[APP] ❌ Answers are irrelevant/wrong. Generating LLM answers instead...")
            print(f"[APP] Validation reason: {validation.get('reason', 'Answers not relevant')}")
            
            # Generate up to 10 LLM answers
            llm_answers = generate_fallback_answer(canonical_q, crop, num_answers=10)
            
            # Format LLM-generated answers
            answers_formatted = []
            for idx, ans in enumerate(llm_answers[:10], 1):
                answers_formatted.append({
                    "text": ans["text"],
                    "confidence": round(float(ans.get("confidence", 0.4)), 4),
                    "rank": idx
                })
            
            print(f"[APP] Generated {len(answers_formatted)} LLM answers to replace irrelevant ones")
            
            disclaimer_msg = "⚠️ The retrieved answers were not relevant to your query. These AI-generated answers are provided as guidance. Please consult local agricultural experts for critical decisions."
            is_validated = False
            validation_reason = f"Retrieved answers were irrelevant: {validation.get('reason', 'Not relevant to query')}. Generated LLM answers instead."
        else:
            # Answers are valid - use them
            print(f"[APP] ✅ Answers validated as relevant ({len(validation.get('validated_answers', []))} valid)")
            # Use validated answers, but if validator didn't return all, use original answers_formatted
            validated_answers = validation.get("validated_answers", [])
            if validated_answers and len(validated_answers) >= len(answers_formatted):
                # Validator returned all or more answers - use them
                answers_formatted = []
                for idx, ans in enumerate(validated_answers[:10], 1):
                    answers_formatted.append({
                        "text": ans["text"],
                        "confidence": round(float(ans["confidence"]), 4),
                        "rank": idx
                    })
            # If validator returned fewer, keep original answers_formatted (already formatted above)
            # This ensures we always have top 10 answers
            
            disclaimer_msg = "This is advisory information based on agricultural data and validated for relevance."
            is_validated = True
            validation_reason = validation.get("reason", "Validation completed - answers are relevant")
        
        response = {
            "translated": translated,
            "original_language": "Unknown",
            "canonical": canonical_q,
            "advice": answers_formatted[0]["text"] if answers_formatted else best.get("best_answer", "No advice available"),
            "confidence": round(float(answers_formatted[0]["confidence"]), 4) if answers_formatted else round(float(best.get("question_score", 0)), 4),
            "all_answers": answers_formatted,
            "matched_question": best.get("question") if best else None,
            "answer_count": len(answers_formatted),
            "source_count": int(best.get("source_count", 0)) if best else 0,
            "disclaimer": disclaimer_msg,
            "is_validated": is_validated,
            "validation_reason": validation_reason
        }
        
        # Reformat advice to user's original language if needed
        if response["advice"]:
            try:
                # Use solution_translator to detect language and reformat answer
                result = generate_farmer_response(user_input, response["advice"])
                print(f"[SOLUTION TRANSLATOR] Result: {result}")
                response["original_language_advice"] = result.get("response", response["advice"])
                response["user_language_type"] = result.get("language_type", "unknown")
                response["original_language"] = result.get("language_type", "Unknown")
                print(f"[SOLUTION TRANSLATOR] Detected language: {result.get('language_type', 'unknown')}")
                print(f"[SOLUTION TRANSLATOR] Reformatted: {response['original_language_advice'][:100] if response['original_language_advice'] else 'None'}")
            except Exception as e:
                print(f"[SOLUTION TRANSLATOR ERROR] {e}, keeping English response")
                response["original_language_advice"] = response["advice"]
                response["user_language_type"] = "unknown"

    print("[RESPONSE]", {
        "translated": response["translated"],
        "original_language": response.get("original_language"),
        "canonical": response["canonical"],
        "confidence": response["confidence"],
        "answer_count": len(response.get("all_answers", [])),
        "all_answers_length": len(response.get("all_answers", [])),
        "is_validated": response.get("is_validated", None)
    })
    print(f"[RESPONSE] Sending {len(response.get('all_answers', []))} answers to frontend")
    
    if request.is_json:
        return jsonify(response)

    return render_template(
        "index.html",
        query=user_input,
        translated=translated,
        canonical=canonical_q,
        response=response
    )


if __name__ == "__main__":
    print("[SERVER] Running at http://127.0.0.1:5000")
    app.run(debug=True)
