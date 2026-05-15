import json
from pathlib import Path

RAW_PATH = Path("app/data/raw/shl_catalog.json")
OUTPUT_PATH = Path("app/data/processed/clean_catalog.json")

# Exclude job solution bundles/suites
INDIVIDUAL_EXCLUSIONS = [
    "solution",
    "bundle",
    "suite"
]


def clean_assessment(item):

    return {
        "entity_id": item.get("entity_id", ""),
        "name": item.get("name", "").strip(),
        "url": item.get("link", "").strip(),
        "description": item.get("description", "").strip(),
        "duration": item.get("duration", "").strip(),
        "languages": item.get("languages", []),
        "job_levels": item.get("job_levels", []),
        "test_types": item.get("keys", []),
        "remote_support": item.get("remote", "no"),
        "adaptive_support": item.get("adaptive", "no"),
    }


def is_individual_assessment(name):

    name_lower = name.lower()

    return not any(
        word in name_lower
        for word in INDIVIDUAL_EXCLUSIONS
    )


def main():

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []

    for item in data:

        cleaned_item = clean_assessment(item)

        # Basic validation
        if not (
            cleaned_item["name"]
            and cleaned_item["url"]
        ):
            continue

        # Filter job solutions/bundles
        if not is_individual_assessment(
            cleaned_item["name"]
        ):
            continue

        cleaned.append(cleaned_item)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cleaned,
            f,
            indent=2
        )

    print(
        f"Saved {len(cleaned)} cleaned assessments"
    )


if __name__ == "__main__":
    main()