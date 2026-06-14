import re
from deep_translator import GoogleTranslator


# =========================
# SOLUTION TRANSLATION FUNCTIONS (NO API - LOCAL ONLY)
# =========================

# Initialize the processor for solution translation
_processor = None

def get_processor():
    """Get or create the multilingual processor instance"""
    global _processor
    if _processor is None:
        _processor = MultilingualQueryProcessor()
    return _processor


def generate_farmer_response(user_query, english_solution):
    """Generate farmer-ready response in user's language"""
    processor = get_processor()
    
    print(f"[SOLUTION TRANSLATOR] Detecting language for: {user_query[:50]}...")
    detected_language = processor.detect_language(user_query)
    lang_code = processor.get_lang_code(detected_language)
    
    print(f"[SOLUTION TRANSLATOR] Detected language: {detected_language}")
    print(f"[SOLUTION TRANSLATOR] Rewriting solution...")
    
    # Translate the solution to the user's language
    if lang_code == "en":
        rewritten = english_solution
    else:
        rewritten = processor.translate(english_solution, "en", lang_code)
    
    print(f"[SOLUTION TRANSLATOR] Rewritten solution: {rewritten[:100] if rewritten else 'None'}...")

    return {
        "language_type": detected_language,
        "response": rewritten
    }


class MultilingualQueryProcessor:
    def __init__(self):
        # Unicode script detection (most reliable)
        self.script_patterns = {
            "telugu": r"[\u0C00-\u0C7F]",
            "tamil": r"[\u0B80-\u0BFF]",
            "hindi": r"[\u0900-\u097F]"
        }

        # Romanized keyword sets (WORD-level only)
        self.roman_keywords = {
            "telugu": {
                "cheyali", "vachay", "emi", "ela", "midha",
                "lo", "maa", "vastunayi", "avuthunnayi", "ga", "unnaru", "nenu"
            },
            "tamil": {
                "enna", "ilai", "aagudhu", "adhukku", "yenna",
                "irukku", "pannunga", "sollunga", "vandhu", "illa"
            },
            "hindi": {
                "mera", "meri", "kya", "karu", "mei", "pei",
                "hai", "hain", "gaye", "raha", "tha", "aap", "kaise"
            }
        }

    # ==================================================
    # 1️⃣ LANGUAGE DETECTION
    # ==================================================
    def detect_language(self, text: str) -> str:
        """
        Detect language based on:
        1. Native script (Telugu/Tamil/Hindi)
        2. Romanized keywords (2+ matches needed)
        3. Default to English
        """
        # Step 1: Native script detection
        for lang, pattern in self.script_patterns.items():
            if re.search(pattern, text):
                # mixed with English letters?
                if re.search(r"[a-zA-Z]", text):
                    return f"{lang}-english"
                return lang

        # Step 2: Romanized detection (word-level)
        words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

        scores = {}
        for lang, keys in self.roman_keywords.items():
            scores[lang] = len(words & keys)

        best_lang = max(scores, key=scores.get)
        if scores[best_lang] >= 2:  # Need at least 2 keyword matches
            return f"{best_lang}-english"

        return "english"

    # ==================================================
    # 2️⃣ LANGUAGE CODE
    # ==================================================
    def get_lang_code(self, detected_lang: str) -> str:
        """Convert detected language to translator language code"""
        return {
            "telugu": "te",
            "tamil": "ta",
            "hindi": "hi",
            "telugu-english": "te",
            "tamil-english": "ta",
            "hindi-english": "hi",
            "english": "en"
        }.get(detected_lang, "en")

    # ==================================================
    # 3️⃣ TRANSLATION
    # ==================================================
    def translate(self, text: str, src: str, tgt: str) -> str:
        """Translate text from source to target language"""
        if src == tgt:
            return text
        try:
            return GoogleTranslator(source=src, target=tgt).translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # safe fallback

    # ==================================================
    # 4️⃣ MAIN PIPELINE
    # ==================================================
    def process_query(self, user_query: str) -> dict:
        """
        Main processing pipeline:
        1. Detect language
        2. Translate to English
        3. Process business logic
        4. Translate response back
        """
        print(f"\n{'='*60}")
        print(f"Original Query: {user_query}")
        print(f"{'='*60}")
        
        detected_lang = self.detect_language(user_query)
        lang_code = self.get_lang_code(detected_lang)
        
        print(f"\nDetected Language: {detected_lang}")
        print(f"Language Code: {lang_code}")

        # Step A: Translate query → English
        english_query = (
            user_query if lang_code == "en"
            else self.translate(user_query, lang_code, "en")
        )
        print(f"\nTranslated Query (English): {english_query}")

        # Step B: Business logic (English only)
        english_response = self.process_business_logic(english_query)
        print(f"\nProcessed Response (English): {english_response}")

        # Step C: Translate response back
        final_response = (
            english_response if lang_code == "en"
            else self.translate(english_response, "en", lang_code)
        )
        print(f"\nFinal Response ({detected_lang}): {final_response}")
        print(f"{'='*60}\n")

        return {
            "original_query": user_query,
            "detected_language": detected_lang,
            "english_query": english_query,
            "english_response": english_response,
            "final_response": final_response
        }

    # ==================================================
    # 5️⃣ BUSINESS LOGIC (REPLACE WITH YOUR LOGIC)
    # ==================================================
    def process_business_logic(self, query: str) -> str:
        """
        Replace this with your actual business logic
        (API calls, database queries, ML models, etc.)
        """
        q = query.lower()

        # Greeting responses
        if "hello" in q or "hi" in q:
            return "Hello! How can I help you today?"
        
        if "name" in q:
            return "I am a multilingual agricultural assistant. I can help you in Telugu, Tamil, Hindi, and English!"

        # Agricultural advisory
        if "curl" in q and ("leaf" in q or "leaves" in q):
            return (
                "Leaf curling with yellowing can indicate: "
                "1) Aphid or whitefly infestation - check underside of leaves, "
                "2) Viral disease like leaf curl virus - remove affected plants, "
                "3) Water stress or nutrient deficiency - ensure proper watering and add balanced fertilizer, "
                "4) Environmental stress from extreme temperatures. "
                "Spray neem oil for pests and improve growing conditions."
            )

        if "yellow" in q and ("leaf" in q or "leaves" in q or "spot" in q):
            return (
                "Yellow leaves or spots can indicate nutrient deficiency (nitrogen or magnesium), "
                "overwatering, pest infestation, or disease. "
                "Check soil moisture, inspect for pests, and consider applying balanced fertilizer. "
                "If spots are present, it might be a fungal infection - "
                "remove affected leaves and use appropriate fungicide."
            )

        if "chilli" in q or "chili" in q or "pepper" in q:
            return (
                "For chilli plant issues: Yellow curling leaves often indicate aphids, whiteflies, or thrips. "
                "Check for pests on leaf undersides. Could also be viral infection (chilli leaf curl virus). "
                "Remove severely affected leaves, spray neem oil or insecticidal soap, "
                "ensure good air circulation, and avoid overwatering."
            )

        if "tomato" in q:
            return (
                "For tomato issues: Yellow spots can indicate early blight, septoria leaf spot, or bacterial speck. "
                "Remove affected leaves, ensure good air circulation, avoid overhead watering, "
                "and apply copper-based fungicide or neem oil. Water at the base of plants in the morning."
            )

        if "gourd" in q:
            return (
                "For gourd yellowing: This could be due to downy mildew, powdery mildew, or nutrient deficiency. "
                "Ensure proper spacing for air flow, remove affected leaves, apply potassium-rich fertilizer, "
                "and use fungicide if needed. Check for whiteflies or aphids which can spread viral diseases."
            )

        if "cabbage" in q:
            return (
                "For cabbage leaf issues: Yellow spots may indicate black rot, downy mildew, or nutrient deficiency. "
                "Remove affected leaves, improve drainage, ensure proper spacing, "
                "and apply copper fungicide or neem oil. Avoid overhead irrigation."
            )

        # Default response
        return (
            f"I received your query: '{query}'. "
            "This is a demo response. Please replace the process_business_logic() method "
            "with your actual agricultural advisory logic, database queries, or API calls."
        )


# ==================================================
# 6️⃣ EXAMPLE USAGE & TESTING
# ==================================================
if __name__ == "__main__":
    processor = MultilingualQueryProcessor()

    # Test cases covering all scenarios
    test_queries = [
        # Native scripts
        "నమస్కారం, మీరు ఎలా ఉన్నారు?",  # Pure Telugu
        "வணக்கம், எப்படி இருக்கிறீர்கள்?",  # Pure Tamil
        "नमस्ते, आप कैसे हैं?",  # Pure Hindi
        "క్యాబేజీ ఆకులపై పసుపు మచ్చలు వచ్చాయి",  # Telugu
        "மிளகாய் செடியின் இலைகள் மஞ்சளாக மாறுகின்றன",  # Tamil
        
        # Pure English
        "Hello, how are you?",
        "Leaves of chilli plant are curling and turning yellow.",
        "What should I do if yellow spots appear on cabbage leaves?",
        
        # Romanized (Transliterated)
        "spine gourd il ilai yellow aagudhu adhukku enna solution",  # Tamil-English
        "mera tomato field mei tomatoes pei yellow spots aa raha hu",  # Hindi-English
        "maa tomato field lo tomatoes midha yellow spots vastunayi",  # Telugu-English
        "cabbage midha yellow spots vachay yem cheyali",  # Telugu-English
        
        # Mixed native + English
        "నేను weather గురించి తెలుసుకోవాలి",  # Telugu-English mixed
    ]

    print("=" * 60)
    print("MULTILINGUAL QUERY PROCESSOR - TEST SUITE")
    print("=" * 60)

    for query in test_queries:
        result = processor.process_query(query)

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

    # Interactive mode
    print("\n\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print("Enter queries in any language:")
    print("- Telugu (తెలుగు) / Tamil (தமிழ்) / Hindi (हिंदी)")
    print("- English")
    print("- Romanized/Transliterated (Tenglish/Tanglish/Hinglish)")
    print("- Mixed languages")
    print("\nType 'exit' to quit\n")

    while True:
        user_input = input("Your Query: ").strip()

        if user_input.lower() == 'exit':
            print("\nGoodbye! 👋")
            break

        if user_input:
            processor.process_query(user_input)