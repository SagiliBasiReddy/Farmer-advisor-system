# translator_fixed.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env")

def translate(text: str):
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
                    "You are a translation engine that converts mixed Indian languages "
                    "(Telugu-English, Hindi-English, Tamil-English, Hinglish, Tanglish, Teluglish) "
                    "into clear ENGLISH.\n"
                    "- Understand phonetic spellings.\n"
                    "- Keep meaning exactly same.\n"
                    "- Output ONLY the translated English text.\n"
                    "- Do NOT explain.\n"
                )
            },
            {"role": "user", "content": text},
        ],
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return data["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    print(translate("paddy il brown spots vannu mazhaykku shesham")) 
