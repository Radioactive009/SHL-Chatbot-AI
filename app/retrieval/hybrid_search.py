import json
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="app/data/chroma_db")

collection = client.get_collection("shl_assessments")

with open("app/data/processed/clean_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

documents = [
    f"{item['name']} {item['description']}"
    for item in catalog
]

tokenized_docs = [doc.lower().split() for doc in documents]

bm25 = BM25Okapi(tokenized_docs)


def hybrid_search(query, top_k=5):
    # Semantic Search
    query_embedding = model.encode(query).tolist()

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    semantic_docs = semantic_results["metadatas"][0]

    # BM25 Search
    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_ranked = sorted(
        zip(catalog, bm25_scores),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]

    bm25_docs = [item[0] for item in bm25_ranked]

    # Combine Results
    combined = {}

    for doc in semantic_docs + bm25_docs:
        combined[doc["entity_id"]] = doc

    return list(combined.values())[:top_k]


if __name__ == "__main__":
    results = hybrid_search(
        "Java developer assessment"
    )

    for r in results:
        print(r["name"])