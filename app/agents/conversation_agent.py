import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.retrieval.hybrid_search import hybrid_search

# Load environment variables
load_dotenv(override=True)

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Load system prompt
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


def build_retrieval_context(retrieved):

    retrieval_context = ""

    for item in retrieved:

        retrieval_context += f"""
Assessment Name: {item['name']}
URL: {item['url']}
Description: {item['description']}
Test Types: {item['test_types']}
Job Levels: {item['job_levels']}

"""

    return retrieval_context


def generate_response(messages):

    user_message = messages[-1]["content"]

    # Refusal Layer
    if should_refuse(user_message):

        return {
            "reply": (
                "I can only help with SHL assessment "
                "recommendations and comparisons."
            ),
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

    retrieval_context = build_retrieval_context(retrieved)

    # Prompt
    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{json.dumps(messages, indent=2)}

Retrieved Assessments:
{retrieval_context}

Instructions:
- Recommend the most relevant SHL assessments
- Explain briefly why each assessment fits
- Keep the response concise and recruiter-friendly
- Do NOT output JSON
- Do NOT invent assessments
"""

    # Groq API Call
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    # Clean Reply
    clean_reply = (
        response.choices[0]
        .message
        .content
        .strip()
    )

    # Recommendation Objects
    recommendations = []

    for item in retrieved:

        recommendations.append({
            "name": item["name"],
            "url": item["url"]
        })

    return {
        "reply": clean_reply,
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