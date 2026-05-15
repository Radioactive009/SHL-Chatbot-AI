import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from app.retrieval.hybrid_search import hybrid_search

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.0-flash")


SYSTEM_PROMPT = open(
    "app/prompts/system_prompt.txt",
    "r",
    encoding="utf-8"
).read()


def detect_intent(user_message):

    message = user_message.lower()

    if "difference" in message or "compare" in message:
        return "compare"

    if "also" in message or "add" in message:
        return "refine"

    if len(message.split()) < 4:
        return "clarify"

    return "recommend"


def should_refuse(user_message):

    blocked_topics = [
        "salary",
        "politics",
        "religion",
        "legal advice",
        "girlfriend",
        "boyfriend"
    ]

    message = user_message.lower()

    return any(
        topic in message
        for topic in blocked_topics
    )


def generate_response(messages):

    user_message = messages[-1]["content"]

    # Refusal Layer
    if should_refuse(user_message):

        return {
            "reply": "I can only help with SHL assessment recommendations and comparisons.",
            "recommendations": [],
            "end_of_conversation": False
        }

    # Intent Detection
    intent = detect_intent(user_message)

    # Clarification Handling
    if intent == "clarify":

        return {
            "reply": (
                "Could you provide more details about the role, "
                "experience level, or skills you want to assess?"
            ),
            "recommendations": [],
            "end_of_conversation": False
        }

    # Retrieval
    retrieved = hybrid_search(user_message, top_k=5)

    retrieval_context = ""

    for item in retrieved:

        retrieval_context += f"""
        Assessment Name: {item['name']}
        URL: {item['url']}
        Description: {item['description']}
        Test Types: {item['test_types']}
        Job Levels: {item['job_levels']}
        """

    prompt = f"""
    {SYSTEM_PROMPT}

    Conversation:
    {json.dumps(messages, indent=2)}

    Retrieved Assessments:
    {retrieval_context}

    Generate a grounded recruiter-friendly response.
    """

    response = model.generate_content(prompt)

    recommendations = []

    for item in retrieved:

        recommendations.append({
            "name": item["name"],
            "url": item["url"]
        })

    return {
        "reply": response.text,
        "recommendations": recommendations,
        "end_of_conversation": False
    }


if __name__ == "__main__":

    test_messages = [
        {
            "role": "user",
            "content": "Hiring a Java backend developer"
        }
    ]

    result = generate_response(test_messages)

    print(json.dumps(result, indent=2))