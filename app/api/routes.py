from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.agents.conversation_agent import generate_response

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@router.get("/health")
def health_check():

    return {
        "status": "ok"
    }


@router.post("/chat")
def chat(request: ChatRequest):

    messages = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in request.messages
    ]

    response = generate_response(messages)

    return response