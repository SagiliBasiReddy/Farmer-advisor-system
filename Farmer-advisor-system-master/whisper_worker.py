import sys
import json
import whisper
import torch


def log(message: str) -> None:
    """Log messages to stderr so stdout stays clean for JSON only."""
    print(message, file=sys.stderr, flush=True)


LANGUAGE_NAMES = {
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "en": "English",
    "bn": "Bengali",
    "gu": "Gujarati",
    "mr": "Marathi",
    "pa": "Punjabi",
    "ur": "Urdu",
}


def get_device():
    """Return the best device to use ('cuda' if available, else 'cpu')."""
    has_cuda = torch.cuda.is_available()
    if has_cuda:
        try:
            name = torch.cuda.get_device_name(0)
        except Exception:
            name = "Unknown CUDA device"
        log(f"[WORKER] CUDA available: True, device: {name}")
        return "cuda"
    else:
        log("[WORKER] CUDA available: False, using CPU")
        return "cpu"


def detect_language(audio_path: str, device: str):
    """
    Step 1: Detect language using Whisper base model.
    Returns (language_code, language_name, confidence_percent_float).
    """
    log(f"[WORKER] Loading base model for language detection on device={device}")
    base_model = whisper.load_model("base", device=device)

    log(f"[WORKER] Loading audio from: {audio_path}")
    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(base_model.device)

    log("[WORKER] Running language detection...")
    _, probs = base_model.detect_language(mel)

    detected = max(probs, key=probs.get)
    confidence = float(probs[detected]) * 100.0

    language_name = LANGUAGE_NAMES.get(detected, detected.upper())

    log(
        f"[WORKER] Detected language: {language_name} ({detected}), "
        f"confidence: {confidence:.2f}%"
    )

    return detected, language_name, confidence


def transcribe_audio(audio_path: str, language_code: str, device: str):
    """
    Step 2: Transcribe using Whisper large-v3 model with fp16=True.
    """
    log(f"[WORKER] Loading large-v3 model for transcription on device={device}")
    model = whisper.load_model("large-v3", device=device)

    use_fp16 = device == "cuda"
    log(f"[WORKER] Transcribing audio in language: {language_code}, fp16={use_fp16}")
    result = model.transcribe(audio_path, language=language_code, fp16=use_fp16)

    text = result.get("text", "").strip()
    log(f"[WORKER] Transcription length: {len(text)} characters")
    return text


def main():
    try:
        if len(sys.argv) < 2:
            raise ValueError("Audio file path must be provided as first argument")

        audio_path = sys.argv[1]

        # Decide device (GPU vs CPU)
        device = get_device()

        # Step 1: Detect language
        lang_code, lang_name, confidence = detect_language(audio_path, device)

        # Step 2: Transcribe
        transcribed_text = transcribe_audio(audio_path, lang_code, device)

        # Step 3: Output JSON ONLY to stdout
        result = {
            "transcribed_text": transcribed_text,
            "language_code": lang_code,
            "language_name": lang_name,
            "confidence": round(confidence, 2),
        }

        # IMPORTANT: stdout must contain ONLY this JSON.
        # Use ensure_ascii=True so Windows consoles don't crash on non-ASCII (e.g., Telugu).
        json_str = json.dumps(result, ensure_ascii=True)
        sys.stdout.write(json_str)
        sys.stdout.flush()

    except Exception as e:
        # On error, output a JSON error object to stdout as well,
        # since the caller depends on JSON.
        error_obj = {
            "error": str(e),
            "transcribed_text": "",
            "language_code": "",
            "language_name": "",
            "confidence": 0.0,
        }
        json_str = json.dumps(error_obj, ensure_ascii=True)
        sys.stdout.write(json_str)
        sys.stdout.flush()
        log(f"[WORKER][ERROR] {e}")


if __name__ == "__main__":
    main()


