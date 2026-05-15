TEST_TYPE_MAP = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Ability & Aptitude": "A",
    "Simulation": "S",
    "Development & 360": "D",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C"
}


def map_test_types(keys):

    short_codes = []

    for key in keys:

        if key in TEST_TYPE_MAP:
            short_codes.append(TEST_TYPE_MAP[key])

    return short_codes