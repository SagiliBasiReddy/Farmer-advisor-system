# language_translator.py

import os
import requests
from langdetect import detect, LangDetectException
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env")

# Map language codes to language names
LANGUAGE_NAMES = {
    'en': 'English',
    'hi': 'Hindi',
    'te': 'Telugu',
    'ta': 'Tamil',
    'kn': 'Kannada',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'as': 'Assamese',
    'gu': 'Gujarati',
    'bn': 'Bengali',
    'pa': 'Punjabi',
}

def detect_language(text: str) -> dict:
    """
    Detect the language of the input text using langdetect + LLM fallback.
    Returns a dict with detected language code and name.
    """
    try:
        lang_code = detect(text)
        
        # If langdetect detected Indonesian (id) or other incorrect languages for Indian text,
        # use LLM to detect properly
        if lang_code in ['id', 'jv', 'my']:  # Indonesian, Javanese, Burmese - often misdetected
            print(f"[LANGUAGE] langdetect returned {lang_code}, using LLM for accurate detection")
            return detect_language_with_llm(text)
        
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
        return {
            "code": lang_code,
            "name": lang_name,
            "confidence": True
        }
    except LangDetectException:
        # If detection fails, use LLM
        return detect_language_with_llm(text)

def detect_language_with_llm(text: str) -> dict:
    """
    Use LLM to detect language when langdetect fails or is incorrect.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a language detection expert. Identify which language the text is in. "
                    "Respond with ONLY the language code (en, hi, te, ta, kn, ml, mr, as, gu, bn, pa) "
                    "or 'mixed' if it's Hinglish/code-mixed. If you can't determine, respond with 'unknown'. "
                    "Example: For 'paddy il brown spots' respond: 'te' (Telugu)\n"
                    "Example: For 'mera farm tomatoes' respond: 'mixed' (Hindi-English mixed)\n"
                    "Example: For 'paddy has brown spots' respond: 'en' (English)"
                )
            },
            {"role": "user", "content": text},
        ],
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            lang_code = response.json()["choices"][0]["message"]["content"].strip().lower()
            
            # Handle special case for mixed language
            if lang_code == "mixed":
                return {
                    "code": "mixed",
                    "name": "Hindi-English Mixed (Hinglish)",
                    "confidence": True
                }
            
            lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.upper())
            return {
                "code": lang_code,
                "name": lang_name,
                "confidence": True
            }
    except Exception as e:
        print(f"[LLM LANGUAGE DETECTION ERROR] {e}")
    
    # Final fallback
    return {
        "code": "unknown",
        "name": "Indian Language (Mixed)",
        "confidence": False
    }

def translate_to_english(text: str) -> str:
    """
    Translate text to English using OpenRouter API.
    Handles mixed Indian languages, phonetic spellings, and Hinglish.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a translation engine for agricultural queries. Convert mixed Indian languages "
                    "(Telugu, Hindi, Tamil, Marathi, Assamese, Hinglish, Tanglish, Teluglish) "
                    "into clear, professional ENGLISH.\n"
                    "- Understand phonetic spellings and local language patterns.\n"
                    "- Keep agricultural meaning exactly the same.\n"
                    "- Output ONLY the translated English text, no explanations.\n"
                    "- Use proper agricultural terminology.\n"
                    "- Example: 'paddy il brown spots vannu' -> 'brown spots appeared in paddy/rice'\n"
                    "- Example: 'medha purugu' (butterflies/pests) -> specify as insects/pests\n"
                )
            },
            {"role": "user", "content": text},
        ],
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        # Check for API errors
        if response.status_code != 200:
            print(f"[TRANSLATION ERROR] API returned status {response.status_code}: {data}")
            # Fallback: return text as-is if translation fails
            return text
        
        if "choices" not in data or not data["choices"]:
            print(f"[TRANSLATION ERROR] No choices in response: {data}")
            return text
        
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[TRANSLATION ERROR] Exception during translation: {e}")
        return text  # Return original text if translation fails

def translate_to_language(text: str, target_lang_code: str) -> str:
    """
    Translate English text back to the specified language.
    """
    if target_lang_code == "en" or target_lang_code == "unknown":
        return text  # Already in English or unable to translate back
    
    target_lang_name = LANGUAGE_NAMES.get(target_lang_code, target_lang_code.upper())
    
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a translator specializing in agricultural terminology. "
                    f"Translate the following English agricultural text to {target_lang_name}.\n"
                    f"- Maintain agricultural accuracy.\n"
                    f"- Use natural, colloquial {target_lang_name} if applicable.\n"
                    f"- Output ONLY the translated text, no explanations."
                )
            },
            {"role": "user", "content": text},
        ],
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return data["choices"][0]["message"]["content"].strip()

def process_query_with_language(text: str, hint_language: str = "") -> dict:
    """
    Main function that detects language, translates to English, 
    and optionally back to original language.
    
    Args:
        text: The user input text
        hint_language: Optional language hint from frontend transcription (e.g., "Hindi")
    
    Returns a dict with:
    - original: Original user input
    - detected_language: Detected language info
    - english: Translated to English
    - original_lang: Translated back to original language (if applicable)
    """
    # Detect language
    lang_info = detect_language(text)
    
    # If we got a language hint from frontend, use it
    if hint_language:
        print(f"[LANGUAGE] Using hint: {hint_language}")
        # Try to find matching language code
        for code, name in LANGUAGE_NAMES.items():
            if name.lower() == hint_language.lower():
                lang_info["code"] = code
                lang_info["name"] = name
                lang_info["confidence"] = True
                break
    
    # Translate to English
    english_text = translate_to_english(text)
    
    # If original is not English, translate advice back to original language
    original_lang_text = None
    if lang_info["code"] != "en" and lang_info["code"] != "unknown":
        try:
            original_lang_text = translate_to_language(english_text, lang_info["code"])
        except Exception as e:
            print(f"Error translating back to {lang_info['name']}: {e}")
            original_lang_text = None
    
    return {
        "original": text,
        "detected_language": lang_info,
        "english": english_text,
        "original_lang": original_lang_text
    }

if __name__ == "__main__":
    # Test examples
    test_queries = [
        "paddy il brown spots vannu mazhaykku shesham",
        "मेरे खेत में भूरे धब्बे आ गए हैं",
        "My rice field has brown spots",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = process_query_with_language(query)
        print(f"Detected: {result['detected_language']}")
        print(f"English: {result['english']}")
        if result['original_lang']:
            print(f"Original: {result['original_lang']}")
