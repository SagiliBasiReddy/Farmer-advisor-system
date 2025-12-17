# summarizer.py
# Extracts crop, symptoms, conditions, and clean summary using OpenRouter

import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: Add OPENROUTER_API_KEY to .env file")

def summarize(text: str):
    """
    Summarizes agricultural issues without hallucination.
    Extracts:
    - crop
    - symptoms
    - conditions (rain, water, drought, etc.)
    - short English summary
    """

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",  # works well for structured outputs
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an agricultural summarizer.\n"
                    "Extract ONLY the information present in the user's text.\n"
                    "Do NOT add disease names or causes that are not mentioned.\n"
                    "Return output ONLY in this JSON format:\n\n"
                    "{\n"
                    "  \"crop\": \"...\",\n"
                    "  \"symptoms\": [\"...\"],\n"
                    "  \"conditions\": [\"...\"],\n"
                    "  \"summary\": \"...\"\n"
                    "}\n\n"
                    "If a field is missing, return null or empty list.\n"
                )
            },
            {"role": "user", "content": text}
        ],
        "temperature": 0.1  # stable, no hallucinations
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return f"❌ API Error: {data}"


# ---------------------------
# Example
# ---------------------------
if __name__ == "__main__":
    text = "Brown spots appeared on the paddy after the rain, and the plants have become weak."
    print(summarize(text))
