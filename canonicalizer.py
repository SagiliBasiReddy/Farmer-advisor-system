import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = """
You are a query rewriter for an agricultural advisory system.

Rewrite the user query into ONE canonical question
matching the dataset style.

Rules:
- Do NOT answer the question.
- Do NOT add new information.
- Do NOT change the crop name.
- Use ONLY information present in the user query.

Allowed formats:


Output ONLY the rewritten question.
"""

EXAMPLES = [
    ("when should tomato be sown", "asking about the sowing time of tomato"),
    ("leaf turning yellow in spine gourd what to do", "asking about control of yellowing of leaf in spine gourd"),
    ("bitter gourd fertilizer per bigha", "asking about the fertilizer dose of bitter gourd"),
    ("marigold diseases", "asking about disease in marigold"),
    ("my cow is not eating grass", "asking about cow not eating grass"),
]


def canonicalize(query: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for u, a in EXAMPLES:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": query})

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(URL, json=payload, headers=headers)
    return r.json()["choices"][0]["message"]["content"].strip()
