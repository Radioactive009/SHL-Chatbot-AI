TEST_TYPE_MAP = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Ability & Aptitude": "A",
    "Simulation": "S",
    "Development & 360": "D",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C"
}


def infer_from_name(name):

    name = name.lower()

    if "opq" in name:
        return ["P"]

    if "personality" in name:
        return ["P"]

    if "sales transformation" in name:
        return ["P"]

    if "verify" in name:
        return ["A"]

    if "numerical" in name:
        return ["A"]

    if "verbal" in name:
        return ["A"]

    return ["K"]


def map_test_types(
    keys,
    assessment_name=""
):

    # Use catalog metadata first
    if keys:

        short_codes = []

        for key in keys:

            if key in TEST_TYPE_MAP:

                short_codes.append(
                    TEST_TYPE_MAP[key]
                )

        if short_codes:
            return short_codes

    # Fallback intelligent inference
    return infer_from_name(
        assessment_name
    )