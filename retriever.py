import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi

df = pd.read_csv("farmers_call_query_data.csv")
df["questions"] = df["questions"].fillna("").astype(str)
df["answers"] = df["answers"].fillna("").astype(str)

tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
tfidf_matrix = tfidf.fit_transform(df["questions"])

tokenized_questions = [q.lower().split() for q in df["questions"]]
bm25 = BM25Okapi(tokenized_questions)


def retrieve(query, top_k=5):
    query = query.lower().strip()

    q_vec = tfidf.transform([query])
    tfidf_scores = (tfidf_matrix @ q_vec.T).toarray().ravel()
    bm25_scores = bm25.get_scores(query.split())

    tfidf_norm = tfidf_scores / (np.max(tfidf_scores) + 1e-9)
    bm25_norm = bm25_scores / (np.max(bm25_scores) + 1e-9)

    scores = 0.5 * tfidf_norm + 0.5 * bm25_norm
    top_idx = np.argsort(scores)[::-1][:top_k]

    candidates = []
    for i in top_idx:
        candidates.append({
            "question": df.iloc[i]["questions"],
            "answers": df.iloc[i]["answers"],
            "score": float(scores[i])
        })

    return candidates
