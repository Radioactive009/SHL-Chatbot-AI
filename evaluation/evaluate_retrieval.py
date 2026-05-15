import json

from app.retrieval.hybrid_search import hybrid_search


def evaluate():

    with open(
        "evaluation/test_queries.json",
        "r",
        encoding="utf-8"
    ) as f:

        test_cases = json.load(f)

    total = 0
    successful = 0

    for case in test_cases:

        query = case["query"]
        expected = case["expected_keywords"]

        results = hybrid_search(query, top_k=5)

        names = " ".join(
            r["name"]
            for r in results
        ).lower()

        hit = any(
            keyword.lower() in names
            for keyword in expected
        )

        total += 1

        if hit:
            successful += 1

        print("\nQUERY:", query)
        print("HIT:", hit)

        for r in results:
            print("-", r["name"])

    recall_at_5 = successful / total

    print("\nRecall@5:", recall_at_5)


if __name__ == "__main__":
    evaluate()