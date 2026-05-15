import json
import chromadb
from pathlib import Path

EMBEDDINGS_PATH = Path("app/data/embeddings/catalog_embeddings.json")

client = chromadb.PersistentClient(path="app/data/chroma_db")

collection = client.get_or_create_collection(
    name="shl_assessments"
)


def clean_metadata(metadata):
    cleaned = {}

    for key, value in metadata.items():

        # Convert lists to comma-separated strings
        if isinstance(value, list):
            cleaned[key] = ", ".join(value) if value else "N/A"

        # Replace empty strings
        elif value == "":
            cleaned[key] = "N/A"

        else:
            cleaned[key] = value

    return cleaned


def main():
    with open(EMBEDDINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:

        cleaned_metadata = clean_metadata(
            item["metadata"]
        )

        collection.add(
            ids=[str(item["id"])],
            embeddings=[item["embedding"]],
            documents=[item["document"]],
            metadatas=[cleaned_metadata]
        )

    print(f"Stored {len(data)} assessments in ChromaDB")


if __name__ == "__main__":
    main()