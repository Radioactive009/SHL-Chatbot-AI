import os
import json

from dotenv import load_dotenv
from groq import Groq

from app.retrieval.hybrid_search import hybrid_search
from app.utils.test_type_mapper import map_test_types

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

    # Comparison
    if "difference" in message or "compare" in message:
        return "compare"

    # Refinement detection
    refinement_keywords = [
        "also",
        "add",
        "include",
        "remove",
        "replace",
        "instead",
        "another"
    ]

    if any(
        keyword in message
        for keyword in refinement_keywords
    ):
        return "refine"

    # Clarification
    vague_queries = [
        "test",
        "assessment",
        "need assessment",
        "need test",
        "hiring",
        "hiring test",
        "hiring assessment",
        "i want test",
        "i want assessment"
    ]

    if message.strip() in vague_queries:
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


def extract_comparison_entities(message):

    message = message.lower()

    aliases = {
        "gsa": "global skills assessment",
        "opq": "occupational personality questionnaire"
    }

    cleaned = (
        message
        .replace("compare", "")
        .replace("difference between", "")
        .replace(",", " and ")
    )

    parts = cleaned.split("and")

    entities = []

    for part in parts:

        entity = part.strip()

        if entity in aliases:
            entity = aliases[entity]

        if entity:
            entities.append(entity)

    return entities


def build_retrieval_context(retrieved):

    retrieval_context = ""

    for item in retrieved:

        retrieval_context += f"""
Assessment Name: {item['name']}
URL: {item['url']}
Description: {item['description']}
Test Types: {item['test_types']}
Job Levels: {item['job_levels']}
Duration: {item.get('duration', 'N/A')}

"""

    return retrieval_context


def deduplicate_results(results):

    seen = set()
    unique_results = []

    for item in results:

        entity_id = item.get("entity_id")

        if entity_id not in seen:

            seen.add(entity_id)
            unique_results.append(item)

    return unique_results


def get_conversation_context(messages):

    previous_user_messages = []

    for msg in messages:

        if msg["role"] == "user":

            previous_user_messages.append(
                msg["content"]
            )

    return " ".join(
        previous_user_messages
    )


def should_include_recommendation(
    query,
    assessment_name
):

    query_lower = query.lower()
    name_lower = assessment_name.lower()

    # Python filtering
    if "python" in query_lower:

        allowed_terms = [
            "python",
            "programming",
            "automata",
            "coding",
            "developer"
        ]

        if not any(
            term in name_lower
            for term in allowed_terms
        ):
            return False

    # Java filtering
    if "java" in query_lower:

        allowed_terms = [
            "java",
            "programming",
            "developer",
            "j2ee"
        ]

        if not any(
            term in name_lower
            for term in allowed_terms
        ):
            return False

    # React filtering
    if "react" in query_lower:

        allowed_terms = [
            "react",
            "javascript",
            "frontend",
            "node",
            "express"
        ]

        if not any(
            term in name_lower
            for term in allowed_terms
        ):
            return False

    return True


def generate_response(messages):

    user_message = messages[-1]["content"]

    conversation_context = (
        get_conversation_context(
            messages
        )
    )

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

    # Retrieval Logic
    if intent == "compare":

        entities = extract_comparison_entities(
            user_message
        )

        retrieved = []

        for entity in entities:

            retrieved.extend(
                hybrid_search(
                    entity,
                    top_k=3
                )
            )

        retrieved = deduplicate_results(
            retrieved
        )

    else:

        # Use full conversation context
        retrieved = hybrid_search(
            conversation_context,
            top_k=5
        )

    # Build Context
    retrieval_context = build_retrieval_context(
        retrieved
    )

    # Prompt
    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{json.dumps(messages, indent=2)}

Retrieved Assessments:
{retrieval_context}

Instructions:
- Recommend ONLY retrieved SHL assessments
- Explain briefly why each assessment fits
- Keep responses concise and recruiter-friendly
- If comparison is requested, compare assessments directly
- Prioritize the most relevant technical matches
- Avoid weak or unrelated recommendations
- Use previous conversation context when refining recommendations
- Format recommendations as a markdown table
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
        temperature=0.2
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

    seen_names = set()

    for item in retrieved:

        name = item["name"]

        # Prevent duplicates
        if name in seen_names:
            continue

        # Filter weak recommendations
        if not should_include_recommendation(
            conversation_context,
            name
        ):
            continue

        seen_names.add(name)

        recommendations.append({
            "name": name,
            "url": item["url"],
            "test_type": map_test_types(
                item.get("test_types", []),
                item.get("name", "")
            )
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
            "content": "Need assessments for Java backend developer"
        },
        {
            "role": "user",
            "content": "Also add cognitive tests"
        }
    ]

    result = generate_response(
        test_messages
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )