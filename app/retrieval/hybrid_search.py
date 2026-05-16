import json
import re
import chromadb

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# Embedding Model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ChromaDB
client = chromadb.PersistentClient(
    path="app/data/chroma_db"
)

collection = client.get_collection(
    "shl_assessments"
)

# Load Catalog
with open(
    "app/data/processed/clean_catalog.json",
    "r",
    encoding="utf-8"
) as f:

    catalog = json.load(f)


# -----------------------------
# TEXT CLEANING
# -----------------------------
def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# -----------------------------
# BM25 DOCUMENTS
# -----------------------------
documents = [

    f"""
    {item['name']}
    {item['description']}
    {' '.join(item.get('test_types', []))}
    {' '.join(item.get('job_levels', []))}
    """

    for item in catalog
]

tokenized_docs = [

    clean_text(doc).split()

    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)


# -----------------------------
# KEYWORD OVERLAP
# -----------------------------
def compute_keyword_overlap(
    query,
    text
):

    query_words = set(
        clean_text(query).split()
    )

    text_words = set(
        clean_text(text).split()
    )

    overlap = query_words.intersection(
        text_words
    )

    return len(overlap)


# -----------------------------
# HYBRID SEARCH
# -----------------------------
def hybrid_search(
    query,
    top_k=10
):

    # -------------------------
    # SEMANTIC SEARCH
    # -------------------------
    query_embedding = model.encode(
        query
    ).tolist()

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 4
    )

    semantic_docs = semantic_results[
        "metadatas"
    ][0]

    # -------------------------
    # BM25 SEARCH
    # -------------------------
    tokenized_query = clean_text(
        query
    ).split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    bm25_ranked = sorted(
        zip(catalog, bm25_scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k * 4]

    # -------------------------
    # COMBINED SCORING
    # -------------------------
    combined_scores = {}

    # Semantic Results
    for rank, doc in enumerate(
        semantic_docs
    ):

        entity_id = doc["entity_id"]

        semantic_score = (
            (top_k * 4) - rank
        )

        keyword_bonus = compute_keyword_overlap(
            query,
            f"""
            {doc.get('name', '')}
            {doc.get('description', '')}
            {' '.join(doc.get('test_types', []))}
            """
        )

        total_score = (
            semantic_score * 2
        ) + keyword_bonus

        combined_scores[entity_id] = {
            "doc": doc,
            "score": total_score
        }

    # BM25 Results
    for rank, (
        doc,
        bm25_score
    ) in enumerate(bm25_ranked):

        entity_id = doc["entity_id"]

        keyword_bonus = compute_keyword_overlap(
            query,
            f"""
            {doc.get('name', '')}
            {doc.get('description', '')}
            {' '.join(doc.get('test_types', []))}
            """
        )

        bm25_final = (
            bm25_score +
            keyword_bonus
        )

        if entity_id in combined_scores:

            combined_scores[entity_id][
                "score"
            ] += bm25_final

        else:

            combined_scores[entity_id] = {
                "doc": doc,
                "score": bm25_final
            }

    # -------------------------
    # FINAL RERANKING
    # -------------------------
    ranked = sorted(
        combined_scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    final_results = []

    seen = set()

    for item in ranked:

        doc = item["doc"]

        entity_id = doc["entity_id"]

        if entity_id in seen:
            continue

        seen.add(entity_id)

        final_results.append(doc)

        if len(final_results) >= top_k:
            break

    return final_results


# -----------------------------
# LOCAL TEST
# -----------------------------
if __name__ == "__main__":

    results = hybrid_search(
        "Python developer assessment"
    )

    print("\nTOP RESULTS:\n")

    for r in results:

        print(
            f"- {r['name']}"
        )