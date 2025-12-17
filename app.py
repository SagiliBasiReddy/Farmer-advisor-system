from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
from flask_cors import CORS

from translator_fixed import translate
from summarizer import summarize
from canonicalizer import canonicalize
from retriever import retrieve
from crop_preference import prefer_crop_specific

app = Flask(__name__, static_folder='agri-advisor/dist', static_url_path='')
CORS(app)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    if os.path.isfile(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/ask", methods=["POST"])
def ask():
    user_input = (
        request.json.get("query", "")
        if request.is_json
        else request.form.get("query", "")
    )

    print("🔹 User:", user_input)

    # 1️⃣ Translate
    translated = translate(user_input)
    print("🔹 English:", translated)

    # 2️⃣ Summarize (for crop only)
    summary = json.loads(summarize(translated))
    print("🔹 Summary:", summary)

    # 3️⃣ Canonical question (KEY STEP)
    canonical_q = canonicalize(translated)
    print("🔹 Canonical Query:", canonical_q)

    # 4️⃣ Retrieve
    candidates = retrieve(canonical_q)

    # 5️⃣ Crop-specific preference
    best = prefer_crop_specific(candidates, summary.get("crop"))

    if not best:
        response = {
            "translated": translated,
            "canonical": canonical_q,
            "advice": "No relevant advisory found.",
            "confidence": 0.0,
            "disclaimer": "Unable to provide agricultural guidance for this query."
        }
    else:
        response = {
            "translated": translated,
            "canonical": canonical_q,
            "advice": best.get("answers", "No advice available"),
            "confidence": round(best.get("score", 0), 2),
            "disclaimer": "This is advisory information based on agricultural data."
        }

    print("📤 Response:", response)
    
    if request.is_json:
        return jsonify(response)

    return render_template(
        "index.html",
        query=user_input,
        translated=translated,
        summary=summary,
        canonical=canonical_q,
        response=response
    )


if __name__ == "__main__":
    print("🚀 Server running at http://127.0.0.1:5000")
    app.run(debug=True)
