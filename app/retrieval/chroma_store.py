import json
import chromadb
from pathlib import Path

EMBEDDINGS_PATH = Path("app/data/embeddings/catalog_embeddings.json")

client = chromadb.PersistentClient(path="app/data/chroma_db")

collection = client.get_or_create_collection(
    name="shl_assessments"
)


def main():
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        collection.add(
            ids=[item["id"]],
            embeddings=[item["embedding"]],
            documents=[item["document"]],
            metadatas=[item["metadata"]]
        )

    print(f"Stored {len(data)} assessments in ChromaDB")


if __name__ == "__main__":
    main()