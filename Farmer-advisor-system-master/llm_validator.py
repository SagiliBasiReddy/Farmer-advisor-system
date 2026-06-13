"""
LLM Validator to check if retrieved answers are reasonable for agricultural queries.
Uses OpenAI API or similar LLM service to validate answers.
"""

import os
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Support OpenRouter API (primary) or OpenAI API (fallback)
LLM_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL", "https://openrouter.ai/api/v1/chat/completions")
# Default to Gemini 3 Flash Preview (latest preview version)
# Fallback models if Gemini 3 is not available
LLM_MODEL = os.getenv("LLM_MODEL", "google/gemini-3-flash-preview")
FALLBACK_MODELS = [
    "google/gemini-2.5-flash",  # Stable Gemini 2.5 version
    "google/gemini-1.5-flash",  # Stable Gemini 1.5 version
    "google/gemini-1.5-pro",    # Gemini Pro version
    "openai/gpt-3.5-turbo",     # OpenAI fallback
    "anthropic/claude-3-haiku"   # Anthropic fallback
]


def validate_answers(query: str, answers: List[Dict], crop: Optional[str] = None) -> Dict:
    """
    Validate if the retrieved answers are reasonable for the given query.
    
    Args:
        query: The canonical query
        answers: List of answer dictionaries with 'text' and 'confidence'
        crop: Optional crop name from summary
    
    Returns:
        Dict with:
            - is_valid: bool
            - validated_answers: List of validated answers
            - reason: str explaining validation result
    """
    if not LLM_API_KEY:
        print("[VALIDATOR] No API key found, skipping validation")
        return {
            "is_valid": True,  # Default to valid if no validator available
            "validated_answers": answers,
            "reason": "Validation skipped - no API key configured"
        }
    
    if not answers or len(answers) == 0:
        return {
            "is_valid": False,
            "validated_answers": [],
            "reason": "No answers provided for validation"
        }
    
    # Check for placeholder/error text patterns BEFORE validation
    placeholder_patterns = [
        "explained details", "explain details", "details explained", "explained", "details",
        "see above", "as mentioned", "refer to", "check previous", "mentioned above",
        "not available", "n/a", "na", "no answer", "no response", "not provided",
        "pending", "to be updated", "under review", "coming soon", "will be updated",
        "error", "invalid", "null", "undefined", "empty", "blank",
        "please contact", "contact support", "call helpline", "contact us",
        "information not available", "data not available", "answer not found"
    ]
    
    # Filter out obvious placeholder answers
    valid_answers = []
    invalid_count = 0
    for ans in answers:
        answer_lower = ans["text"].lower().strip()
        is_placeholder = any(pattern in answer_lower for pattern in placeholder_patterns)
        # Also check if answer is too short or too generic
        is_too_short = len(answer_lower) < 15  # Less than 15 chars is likely incomplete
        is_too_generic = answer_lower in ["yes", "no", "ok", "sure", "maybe", "thanks", "thank you"]
        # Check if it's just repeating the question or saying nothing useful
        is_non_answer = answer_lower in ["explained", "details", "information", "answer"]
        
        if not (is_placeholder or is_too_short or is_too_generic or is_non_answer):
            valid_answers.append(ans)
        else:
            invalid_count += 1
            print(f"[VALIDATOR] Filtered out placeholder answer: '{ans['text'][:50]}...'")
    
    if len(valid_answers) == 0:
        print(f"[VALIDATOR] All {len(answers)} answers are placeholders/invalid - marking as invalid")
        return {
            "is_valid": False,
            "validated_answers": [],
            "reason": f"All {len(answers)} retrieved answers are placeholders, errors, or too generic (e.g., 'explained details', 'details', etc.)"
        }
    
    if invalid_count > 0:
        print(f"[VALIDATOR] Filtered out {invalid_count} placeholder/invalid answers, {len(valid_answers)} remain for validation")
    
    # Prepare answer text for validation
    answer_texts = [ans["text"] for ans in valid_answers[:5]]  # Validate top 5 valid ones
    answers_str = "\n".join([f"{i+1}. {ans}" for i, ans in enumerate(answer_texts)])
    
    # Create validation prompt - STRICT validation
    crop_context = f" (related to {crop})" if crop else ""
    prompt = f"""You are an agricultural expert validator. Review the following query and answers to determine if they are RELEVANT and CORRECT.

Query: "{query}"{crop_context}

Retrieved Answers:
{answers_str}

STRICTLY evaluate each answer:
1. Is it DIRECTLY relevant to the specific agricultural query asked?
2. Does it answer the question being asked?
3. Is it factually correct for farming/agriculture?
4. Does it provide useful, actionable guidance?

IMPORTANT: Mark as INVALID if:
- Answers are generic/irrelevant to the specific query
- Answers don't address what was asked
- Answers are vague or off-topic
- Answers contain incorrect information
- Answers are placeholders like "explained details", "see above", "not available"
- Answers are too short or incomplete (less than meaningful content)
- Answers don't provide specific, actionable information

Respond in JSON format:
{{
    "is_valid": true/false,
    "validated_count": number of valid answers,
    "reason": "brief explanation of why valid/invalid",
    "validated_answers": [
        {{"text": "answer text", "is_valid": true/false, "reason": "why"}}
    ]
}}

Be STRICT - only mark as valid if answers are directly relevant and correct."""

    # Try primary model first, then fallbacks if it fails
    models_to_try = [LLM_MODEL] + FALLBACK_MODELS
    
    for model_name in models_to_try:
        try:
            # OpenRouter requires HTTP-Referer and X-Title headers
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo",  # Optional but recommended
                "X-Title": "Agricultural Advisory System"  # Optional but recommended
            }
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are an agricultural expert validator. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            print(f"[VALIDATOR] Calling LLM API with model: {model_name}")
            response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=15)
            
            # Check for 400 errors specifically
            if response.status_code == 400:
                error_detail = response.text
                print(f"[VALIDATOR] Model {model_name} returned 400 error: {error_detail[:200]}")
                if model_name != models_to_try[-1]:  # Not the last model
                    print(f"[VALIDATOR] Trying fallback model...")
                    continue  # Try next model
                else:
                    response.raise_for_status()  # Raise if it's the last model
            
            # Check for API credit issues (402, 429, 500)
            if response.status_code in [402, 429, 500, 503]:
                print(f"[VALIDATOR] API temporarily unavailable ({response.status_code}), using fallback validation")
                return {
                    "is_valid": True,
                    "validated_answers": valid_answers,
                    "reason": "Using fallback validation - placeholder answers filtered"
                }
            
            response.raise_for_status()
        
            result = response.json()
            
            # Check if response has choices
            if "choices" not in result or not result["choices"]:
                print(f"[VALIDATOR] No choices in API response, using fallback")
                return {
                    "is_valid": True,
                    "validated_answers": valid_answers,
                    "reason": "Using fallback validation - placeholder answers filtered"
                }
            
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            validation_result = json.loads(content)
            
            # Filter validated answers - use the pre-filtered valid_answers
            validated_list = []
            validation_results = validation_result.get("validated_answers", [])
            
            for i, ans in enumerate(valid_answers):
                if i < len(validation_results):
                    val_ans = validation_results[i]
                    if val_ans.get("is_valid", True):
                        validated_list.append(ans)
                else:
                    # If validator didn't check all, include by default (they passed placeholder check)
                    validated_list.append(ans)
            
            print(f"[VALIDATOR] Successfully validated with {model_name}: {len(validated_list)}/{len(valid_answers)} answers as reasonable (filtered {len(answers) - len(valid_answers)} placeholders)")
            
            return {
                "is_valid": validation_result.get("is_valid", True),
                "validated_answers": validated_list if validated_list else answers[:3],  # Fallback to top 3
                "reason": validation_result.get("reason", "Validation completed"),
                "validated_count": len(validated_list)
            }
            
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400 and model_name != models_to_try[-1]:
                # Try next model if 400 error and not last model
                print(f"[VALIDATOR] Model {model_name} failed with HTTP 400, trying next model...")
                continue
            else:
                # Re-raise if it's the last model or a different error
                if model_name == models_to_try[-1]:
                    raise
                continue
        except json.JSONDecodeError as e:
            print(f"[VALIDATOR] JSON decode error with {model_name}: {e}")
            if model_name != models_to_try[-1]:
                continue  # Try next model
            else:
                return {
                    "is_valid": True,
                    "validated_answers": answers[:5],  # Default to top 5
                    "reason": "Validation response parsing failed, using default"
                }
        except requests.exceptions.RequestException as e:
            print(f"[VALIDATOR] API error with {model_name}: {e}")
            if model_name != models_to_try[-1]:
                continue  # Try next model
            else:
                return {
                    "is_valid": True,
                    "validated_answers": answers[:5],  # Default to top 5
                    "reason": f"Validation API error: {str(e)}"
                }
    
    # If we get here, all models failed
    print(f"[VALIDATOR] All models failed, using default validation")
    return {
        "is_valid": True,
        "validated_answers": answers[:5],  # Default to top 5
        "reason": "All LLM models failed, using retrieved answers as-is"
    }


def generate_fallback_answer(query: str, crop: Optional[str] = None, num_answers: int = 1) -> List[Dict]:
    """
    Generate fallback answer(s) using LLM when retrieved answers are invalid.
    
    Args:
        query: The canonical query
        crop: Optional crop name
        num_answers: Number of answers to generate (default 1, can be up to 10)
    
    Returns:
        List of Dict with 'text' and 'confidence' matching dataset format
    """
    if not LLM_API_KEY:
        return [{
            "text": "I apologize, but I couldn't find specific information for your query. Please consult with a local agricultural expert or extension officer for detailed guidance.",
            "confidence": 0.3
        }]
    
    crop_context = f" related to {crop}" if crop else ""
    
    if num_answers > 1:
        prompt = f"""You are an agricultural advisory assistant. The retrieved answers for this query were not relevant. Generate {num_answers} different, helpful agricultural answers.

Query: "{query}"{crop_context}

Provide {num_answers} practical, relevant answers in the style of agricultural advisory services. Each answer should:
- Be directly relevant to the query
- Provide actionable guidance
- Be concise (under 150 words each)
- Cover different aspects or approaches

Format as JSON array:
[
    {{"text": "first answer", "confidence": 0.7}},
    {{"text": "second answer", "confidence": 0.6}},
    ...
]

Respond ONLY with valid JSON array."""
    else:
        prompt = f"""You are an agricultural advisory assistant. The retrieved answers for this query were not relevant. Provide a helpful, relevant agricultural answer.

Query: "{query}"{crop_context}

Provide a concise, practical answer that directly addresses the query. Keep it under 200 words.
Format your response as plain text suitable for farmers."""

    # Try primary model first, then fallbacks if it fails
    models_to_try = [LLM_MODEL] + FALLBACK_MODELS
    
    for model_name in models_to_try:
        try:
            # OpenRouter requires HTTP-Referer and X-Title headers
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo",  # Optional but recommended
                "X-Title": "Agricultural Advisory System"  # Optional but recommended
            }
            
            max_tokens = 2000 if num_answers > 1 else 300
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are a helpful agricultural advisory assistant. Provide practical, farmer-friendly advice. Respond with valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": max_tokens
            }
            
            print(f"[VALIDATOR] Generating {num_answers} fallback answer(s) via LLM API with model: {model_name}")
            response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=25)
            
            # Check for 400 errors specifically
            if response.status_code == 400:
                error_detail = response.text
                print(f"[VALIDATOR] Model {model_name} returned 400 error: {error_detail[:200]}")
                if model_name != models_to_try[-1]:  # Not the last model
                    print(f"[VALIDATOR] Trying fallback model...")
                    continue  # Try next model
                else:
                    response.raise_for_status()  # Raise if it's the last model
            
            response.raise_for_status()
        
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            if num_answers > 1:
                # Try to parse as JSON array
                try:
                    answers_list = json.loads(content)
                    if isinstance(answers_list, list):
                        formatted_answers = []
                        for idx, ans in enumerate(answers_list[:num_answers]):
                            if isinstance(ans, dict):
                                formatted_answers.append({
                                    "text": ans.get("text", str(ans)),
                                    "confidence": float(ans.get("confidence", 0.5 - (idx * 0.05)))
                                })
                            else:
                                formatted_answers.append({
                                    "text": str(ans),
                                    "confidence": 0.5 - (idx * 0.05)
                                })
                        print(f"[VALIDATOR] Generated {len(formatted_answers)} fallback answers using {model_name}")
                        return formatted_answers
                except json.JSONDecodeError:
                    # Fall through to single answer parsing
                    pass
            
            # Single answer or fallback
            print(f"[VALIDATOR] Generated fallback answer using {model_name} ({len(content)} chars)")
            return [{
                "text": content,
                "confidence": 0.4  # Lower confidence for generated answers
            }]
            
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code') and e.response.status_code == 400 and model_name != models_to_try[-1]:
                # Try next model if 400 error and not last model
                print(f"[VALIDATOR] Model {model_name} failed with HTTP error, trying next model...")
                continue
            else:
                # Re-raise if it's the last model or a different error
                if model_name == models_to_try[-1]:
                    raise
                continue
        except Exception as e:
            print(f"[VALIDATOR] Error with {model_name}: {e}")
            if model_name != models_to_try[-1]:
                continue  # Try next model
            else:
                # Last model failed
                return [{
                    "text": "I apologize, but I couldn't find specific information for your query. Please consult with a local agricultural expert or extension officer for detailed guidance.",
                    "confidence": 0.3
                }]
    
    # If all models failed
    print(f"[VALIDATOR] All models failed for fallback generation")
    return [{
        "text": "I apologize, but I couldn't find specific information for your query. Please consult with a local agricultural expert or extension officer for detailed guidance.",
        "confidence": 0.3
    }]

