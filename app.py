from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
import tempfile
import requests
import base64
from flask_cors import CORS
from dotenv import load_dotenv
from pydub import AudioSegment
import io
import gc

# Load environment variables
load_dotenv()

# Lazy imports to reduce startup time
translator_fixed = None
soltrans = None
retriever_module = None
crop_preference_module = None
llm_validator_module = None
canonicalizer_module = None

def lazy_import_translator():
    global translator_fixed
    if translator_fixed is None:
        from translator_fixed import translate
        translator_fixed = translate
    return translator_fixed

def lazy_import_soltrans():
    global soltrans
    if soltrans is None:
        from soltrans import generate_farmer_response
        soltrans = generate_farmer_response
    return soltrans

def lazy_import_retriever():
    global retriever_module
    if retriever_module is None:
        from retriever import retrieve
        retriever_module = retrieve
    return retriever_module

def lazy_import_crop_preference():
    global crop_preference_module
    if crop_preference_module is None:
        from crop_preference import prefer_crop_specific
        crop_preference_module = prefer_crop_specific
    return crop_preference_module

def lazy_import_llm_validator():
    global llm_validator_module
    if llm_validator_module is None:
        from llm_validator import validate_answers, generate_fallback_answer
        llm_validator_module = (validate_answers, generate_fallback_answer)
    return llm_validator_module

def lazy_import_canonicalizer():
    global canonicalizer_module
    if canonicalizer_module is None:
        from canonicalizer import canonicalize
        canonicalizer_module = canonicalize
    return canonicalizer_module

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__, static_folder='agri-advisor/dist', static_url_path='')
CORS(app, origins="*")

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

LANGUAGE_CODE_TO_NAME = {
    "te-IN": "Telugu",
    "hi-IN": "Hindi",
    "ta-IN": "Tamil",
    "kn-IN": "Kannada",
    "ml-IN": "Malayalam",
    "en-IN": "English",
    "bn-IN": "Bengali",
    "gu-IN": "Gujarati",
    "mr-IN": "Marathi",
    "pa-IN": "Punjabi",
    "or-IN": "Odia",
}


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


def convert_to_wav(audio_bytes, filename):
    """
    Convert any audio format to WAV format for Sarvam API.
    Handles WebM, MP3, and other formats that pydub supports.
    """
    try:
        # Try to detect format from filename
        if filename.endswith('.wav'):
            return audio_bytes
        
        # Try to load as audio and convert to WAV
        try:
            # Try with explicit format first based on filename
            if filename.endswith('.webm'):
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="webm")
            elif filename.endswith('.mp3'):
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            elif filename.endswith('.ogg'):
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="ogg")
            else:
                # Try generic detection
                audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # Convert to WAV
            output = io.BytesIO()
            audio.export(output, format="wav")
            return output.getvalue()
        except Exception as e:
            print(f"[CONVERT] Conversion failed: {str(e)}, trying raw bytes")
            # If conversion fails, return as-is (might already be WAV or compatible)
            return audio_bytes
    except Exception as e:
        print(f"[CONVERT] Error: {str(e)}")
        return audio_bytes


def generate_audio_from_text(text, language_code="en-IN"):
    """
    Generate audio (TTS) from text using Sarvam API.
    Returns base64-encoded audio bytes or None if generation fails.
    """
    if not text or len(text.strip()) == 0:
        return None
    
    if SARVAM_API_KEY is None or not SARVAM_API_KEY.strip():
        print("[TTS] SARVAM_API_KEY is not set, skipping audio generation")
        return None
    
    try:
        print(f"[TTS] Generating audio for language: {language_code}")
        
        # Sarvam Text-to-Speech API endpoint
        tts_url = "https://api.sarvam.ai/text-to-speech"
        
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
        }
        
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "model": "bulbul:v3",
            "speaker": "kavya",  # Female speaker - compatible with bulbul:v3 model
            "pace": 1.0
        }
        
        response = requests.post(tts_url, json=payload, headers=headers, timeout=60)
        
        if not response.ok:
            print(f"[TTS] Error: Status {response.status_code}")
            try:
                error_data = response.json()
                print(f"[TTS] Error response: {error_data}")
            except:
                print(f"[TTS] Error response: {response.text}")
            return None
        
        response_data = response.json()
        
        # Extract audio from response
        if "audios" in response_data and len(response_data["audios"]) > 0:
            audio_content = response_data["audios"][0]
            
            # If audio_content is a string, decode it from base64
            if isinstance(audio_content, str):
                audio_bytes = base64.b64decode(audio_content)
            else:
                audio_bytes = audio_content
            
            # Convert to base64 for response
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            print(f"[TTS] Successfully generated audio, size: {len(audio_bytes)} bytes")
            return audio_base64
        else:
            print("[TTS] No audio in response")
            return None
            
    except Exception as e:
        print(f"[TTS] Error generating audio: {str(e)}")
        return None


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Transcribe audio from user's microphone.
    Expects an audio file in multipart/form-data under the `audio` field.
    Supports WAV, WebM, and other formats via automatic conversion.
    """
    tmp_path = None
    try:
        if SARVAM_API_KEY is None or not SARVAM_API_KEY.strip():
            return jsonify({"success": False, "error": "SARVAM_API_KEY is not set"}), 500

        if "audio" not in request.files:
            return jsonify({"success": False, "error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        if not audio_file or audio_file.filename is None:
            return jsonify({"success": False, "error": "Invalid audio upload"}), 400

        # Read and convert audio to WAV format
        audio_bytes = audio_file.read()
        if not audio_bytes:
            return jsonify({"success": False, "error": "Uploaded audio is empty"}), 400

        print(f"[TRANSCRIBE] Received audio file: {audio_file.filename}, size: {len(audio_bytes)} bytes")

        # Convert to WAV format if needed
        wav_bytes = convert_to_wav(audio_bytes, audio_file.filename)

        # Save as a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name

        print(f"[TRANSCRIBE] WAV file prepared, size: {len(wav_bytes)} bytes")

        sarvam_url = "https://api.sarvam.ai/speech-to-text"
        headers = {
            "api-subscription-key": SARVAM_API_KEY,
        }
        data = {"language_code": "unknown"}

        with open(tmp_path, "rb") as f:
            files = {"file": ("recording.wav", f, "audio/wav")}
            sarvam_resp = requests.post(
                sarvam_url,
                headers=headers,
                data=data,
                files=files,
                timeout=120,
            )

        try:
            sarvam_json = sarvam_resp.json()
        except Exception:
            return jsonify({"success": False, "error": "Sarvam returned non-JSON response"}), 502

        if not sarvam_resp.ok:
            return jsonify({
                "success": False,
                "error": sarvam_json.get("error") or sarvam_json.get("message") or "Sarvam transcription failed",
            }), sarvam_resp.status_code

        transcript = (sarvam_json.get("transcript") or "").strip()
        language_code = sarvam_json.get("language_code") or sarvam_json.get("language") or "unknown"

        # Confidence field name can vary; try a few common shapes.
        confidence = sarvam_json.get("confidence")
        if confidence is None:
            results = sarvam_json.get("results") or sarvam_json.get("result") or []
            if isinstance(results, list) and results:
                confidence = results[0].get("confidence")
            elif isinstance(results, dict):
                confidence = results.get("confidence")

        language_name = LANGUAGE_CODE_TO_NAME.get(language_code, language_code if language_code else "Unknown")

        if not transcript:
            return jsonify({
                "success": False,
                "error": "Sarvam transcription returned an empty transcript",
            }), 502

        print(f"[TRANSCRIBE] Success: {transcript} ({language_name})")

        return jsonify({
            "success": True,
            "transcribed_text": transcript,
            "language_code": language_code,
            "language_name": language_name,
            "confidence": confidence,
        }), 200

    except requests.Timeout:
        return jsonify({"success": False, "error": "Sarvam request timed out"}), 504
    except Exception as e:
        print(f"[TRANSCRIBE] Error: {str(e)}")
        return jsonify({"success": False, "error": f"Transcription failed: {str(e)}"}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                print("[TRANSCRIBE] Temp file deleted")
            except Exception:
                print("[TRANSCRIBE] Warning: temp file could not be deleted")


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for deployment monitoring."""
    return jsonify({
        "status": "ok",
        "message": "Agro Advisor backend is running",
        "timestamp": os.getenv("TIMESTAMP", "N/A")
    }), 200


@app.route("/ask", methods=["POST"])
def ask():
    try:
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

        # Lazy load translator on first use
        translate = lazy_import_translator()
        canonicalize = lazy_import_canonicalizer()
        retrieve = lazy_import_retriever()
        prefer_crop_specific = lazy_import_crop_preference()
        generate_fallback_answer = lazy_import_llm_validator()[1]
        validate_answers = lazy_import_llm_validator()[0]
        generate_farmer_response = lazy_import_soltrans()
        
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
    
    # 🎙️ Generate audio in the original language (if available)
    original_language = response.get("original_language", "Unknown")
    language_code_for_audio = "en-IN"  # Default to English
    
    # Map language names to Sarvam language codes
    language_name_to_code = {
        "Telugu": "te-IN",
        "Hindi": "hi-IN",
        "Tamil": "ta-IN",
        "Kannada": "kn-IN",
        "Malayalam": "ml-IN",
        "English": "en-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Marathi": "mr-IN",
        "Punjabi": "pa-IN",
        "Odia": "or-IN",
    }
    
    # Determine which text to use for TTS (prefer original language advice)
    text_for_tts = response.get("original_language_advice") or response.get("advice", "")
    
    # Get language code from original language
    if original_language and original_language != "Unknown":
        language_code_for_audio = language_name_to_code.get(original_language, "en-IN")
    
    # Generate audio
    if text_for_tts:
        print(f"[TTS] Generating audio in {original_language} ({language_code_for_audio}) for advisory")
        audio_base64 = generate_audio_from_text(text_for_tts, language_code_for_audio)
        
        if audio_base64:
            response["audio_base64"] = audio_base64
            response["audio_language"] = language_code_for_audio
            response["has_audio"] = True
            print(f"[TTS] Audio generated successfully")
        else:
            print(f"[TTS] Audio generation failed, continuing without audio")
            response["has_audio"] = False
    else:
        response["has_audio"] = False
    
    if request.is_json:
        return jsonify(response)

    return render_template(
        "index.html",
        query=user_input,
        translated=translated,
        canonical=canonical_q,
        response=response
    )
    
    except Exception as e:
        print(f"[ERROR] /ask endpoint failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Processing failed: {str(e)}",
            "status": "error"
        }), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV", "production") == "development"
    print(f"[SERVER] Starting Agro Advisor backend on port {port}")
    print(f"[SERVER] Debug mode: {debug_mode}")
    print(f"[SERVER] Visit http://0.0.0.0:{port}/health for health check")
    
    # Force garbage collection on startup
    gc.collect()
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode, threaded=True)
