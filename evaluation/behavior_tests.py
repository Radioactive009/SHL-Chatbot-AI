from app.agents.conversation_agent import generate_response


tests = [

    {
        "input": "Need assessment",
        "expected": "clarification"
    },

    {
        "input": "Compare OPQ and GSA",
        "expected": "comparison"
    },

    {
        "input": "Tell me salary trends",
        "expected": "refusal"
    }
]


def run_tests():

    for test in tests:

        result = generate_response([
            {
                "role": "user",
                "content": test["input"]
            }
        ])

        print("\nINPUT:", test["input"])
        print("REPLY:", result["reply"])


if __name__ == "__main__":
    run_tests()