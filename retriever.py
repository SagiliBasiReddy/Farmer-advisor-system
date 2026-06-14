import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi

# Load cleaned dataset with deduplicated questions and multiple answers
df = pd.read_csv("farmers_call_query_data_cleaned.csv")
df["standardized_question"] = df["standardized_question"].fillna("").astype(str)
df["answers"] = df["answers"].fillna("").astype(str)

print(f"[RETRIEVER] Loaded: {len(df):,} unique questions")

tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
tfidf_matrix = tfidf.fit_transform(df["standardized_question"])

tokenized_questions = [q.lower().split() for q in df["standardized_question"]]
bm25 = BM25Okapi(tokenized_questions)


def retrieve(query, top_k=10, min_score=0.15):
    """
    Retrieve top answers for a query with confidence scoring.
    
    Returns multiple answers per question with individual confidence scores.
    """
    query = query.lower().strip()

    q_vec = tfidf.transform([query])
    tfidf_scores = (tfidf_matrix @ q_vec.T).toarray().ravel()
    bm25_scores = bm25.get_scores(query.split())

    tfidf_norm = tfidf_scores / (np.max(tfidf_scores) + 1e-9)
    bm25_norm = bm25_scores / (np.max(bm25_scores) + 1e-9)

    scores = 0.5 * tfidf_norm + 0.5 * bm25_norm
    
    # Filter by minimum score threshold
    valid_idx = np.where(scores >= min_score)[0]
    
    if len(valid_idx) == 0:
        return []
    
    # Get top k from valid indices
    valid_scores = scores[valid_idx]
    top_local_idx = np.argsort(valid_scores)[::-1][:top_k]
    top_idx = valid_idx[top_local_idx]

    # Placeholder patterns to filter out
    placeholder_patterns = [
        "explained details", "explain details", "details explained", "explained", "details",
        "explain briefly", "explained briefly", "briefly explained",
        "explain in details", "explained in details", "explains details",
        "explained him", "explained her", "explained them",
        "see above", "as mentioned", "refer to", "check previous",
        "not available", "n/a", "na", "no answer", "no response"
    ]
    
    def is_placeholder(text):
        """Check if answer is a placeholder"""
        text_lower = text.lower().strip()
        return any(pattern in text_lower for pattern in placeholder_patterns) or len(text_lower) < 15
    
    candidates = []
    for i in top_idx:
        question_score = float(scores[i])
        
        # Parse multiple answers separated by |||
        answers_text = df.iloc[i]["answers"]
        answer_list = [ans.strip() for ans in answers_text.split("|||") if ans.strip()]
        
        # Filter out placeholder answers
        real_answers = [ans for ans in answer_list if not is_placeholder(ans)]
        
        # If all answers are placeholders, use original list (but mark them)
        if len(real_answers) == 0:
            real_answers = answer_list
            print(f"[RETRIEVER] Warning: All answers for '{df.iloc[i]['standardized_question'][:50]}...' are placeholders")
        
        # Create confidence scores for each answer
        # Real answers get priority, placeholders get lower scores
        answer_details = []
        real_answer_idx = 0
        
        for ans_idx, answer_text in enumerate(answer_list):
            is_placeholder_answer = is_placeholder(answer_text)
            
            if is_placeholder_answer:
                # Placeholder answers get very low confidence
                confidence = question_score * 0.1  # 10% of question score
            else:
                # Real answers get higher confidence based on their position among real answers
                if real_answer_idx == 0:
                    confidence = question_score  # First real answer: 100%
                elif real_answer_idx == 1:
                    confidence = question_score * 0.85  # Second real answer: 85%
                else:
                    confidence = question_score * 0.70  # 3rd+ real answer: 70%
                real_answer_idx += 1
            
            answer_details.append({
                "text": answer_text,
                "confidence": confidence,
                "rank": ans_idx + 1,  # Original rank in dataset
                "is_placeholder": is_placeholder_answer
            })
        
        # Best answer is the first non-placeholder answer, or first answer if all are placeholders
        best_answer = real_answers[0] if real_answers else answer_list[0]
        
        candidates.append({
            "question": df.iloc[i]["standardized_question"],
            "original_questions": df.iloc[i]["original_questions"].split("|||")[0],  # Get first original
            "answer_count": df.iloc[i]["answer_count"],
            "source_count": df.iloc[i]["source_count"],
            "answers": answer_details,  # List of answers with confidence
            "best_answer": best_answer,  # First real answer (not placeholder)
            "question_score": question_score  # Overall match score
        })

    return candidates
