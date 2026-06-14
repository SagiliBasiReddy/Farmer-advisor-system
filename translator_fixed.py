# translator_fixed.py
# Wrapper module for translation functionality

import os
import requests
from langdetect import detect, LangDetectException
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env")

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

def translate_to_english_with_llm(text: str) -> str:
    """
    Translate text to English using OpenRouter API with LLM.
    """
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": "meta-llama/llama-2-7b-chat",
                "messages": [
                    {
                        "role": "user",
                        "content": f"Translate the following text to English. Return only the translated text, nothing else.\n\nText: {text}"
                    }
                ],
                "temperature": 0.3,
            }
        )
        response.raise_for_status()
        result = response.json()
        translated = result["choices"][0]["message"]["content"].strip()
        return translated
    except Exception as e:
        print(f"[TRANSLATION ERROR] {e}")
        return text

def translate(text: str) -> str:
    """
    Translate text to English.
    If text is already in English, returns it as-is.
    Otherwise, uses LLM to translate to English.
    """
    try:
        lang_code = detect(text)
        
        # If already English, return as-is
        if lang_code == 'en':
            return text
        
        # Otherwise, translate to English
        return translate_to_english_with_llm(text)
    except LangDetectException:
        # If detection fails, try translation anyway
        return translate_to_english_with_llm(text)
    except Exception as e:
        print(f"[TRANSLATION ERROR] {e}")
        return text
