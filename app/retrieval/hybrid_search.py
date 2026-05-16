import json
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

# BM25 Documents
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
    doc.lower().split()
    for doc in documents
]

bm25 = BM25Okapi(tokenized_docs)


def compute_keyword_overlap(query, text):

    query_words = set(
        query.lower().split()
    )

    text_words = set(
        text.lower().split()
    )

    return len(
        query_words.intersection(
            text_words
        )
    )


def hybrid_search(query, top_k=5):

    # Semantic Search
    query_embedding = model.encode(
        query
    ).tolist()

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 3
    )

    semantic_docs = semantic_results[
        "metadatas"
    ][0]

    # BM25 Search
    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    bm25_ranked = sorted(
        zip(catalog, bm25_scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k * 3]

    # Combined Scoring
    combined_scores = {}

    # Add Semantic Results
    for rank, doc in enumerate(semantic_docs):

        entity_id = doc["entity_id"]

        semantic_score = (
            top_k * 3 - rank
        )

        keyword_bonus = compute_keyword_overlap(
            query,
            f"""
            {doc.get('name', '')}
            {doc.get('description', '')}
            """
        )

        combined_scores[entity_id] = {
            "doc": doc,
            "score": semantic_score + keyword_bonus
        }

    # Add BM25 Results
    for rank, (doc, bm25_score) in enumerate(bm25_ranked):

        entity_id = doc["entity_id"]

        keyword_bonus = compute_keyword_overlap(
            query,
            f"""
            {doc.get('name', '')}
            {doc.get('description', '')}
            """
        )

        final_score = (
            bm25_score +
            keyword_bonus
        )

        if entity_id in combined_scores:

            combined_scores[entity_id][
                "score"
            ] += final_score

        else:

            combined_scores[entity_id] = {
                "doc": doc,
                "score": final_score
            }

    # Final Reranking
    ranked = sorted(
        combined_scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    final_results = [
        item["doc"]
        for item in ranked[:top_k]
    ]

    return final_results


if __name__ == "__main__":

    results = hybrid_search(
        "Python developer assessment"
    )

    for r in results:
        print(r["name"])