import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

CATALOG_PATH = Path("app/data/processed/clean_catalog.json")
OUTPUT_PATH = Path("app/data/embeddings/catalog_embeddings.json")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def build_search_text(item):
    return f"""
    Name: {item['name']}
    Description: {item['description']}
    Test Types: {', '.join(item['test_types'])}
    Job Levels: {', '.join(item['job_levels'])}
    Duration: {item['duration']}
    Languages: {', '.join(item['languages'])}
    """


def main():
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    embedded_data = []

    for item in catalog:
        search_text = build_search_text(item)

        embedding = model.encode(search_text).tolist()

        embedded_data.append({
            "id": item["entity_id"],
            "embedding": embedding,
            "metadata": item,
            "document": search_text
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f)

    print(f"Embedded {len(embedded_data)} assessments")


if __name__ == "__main__":
    main()