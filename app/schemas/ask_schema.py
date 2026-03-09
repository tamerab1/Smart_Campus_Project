# app/schemas/ask_schema.py
from pydantic import BaseModel
from typing import List, Optional

class MessageHistory(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    question: str
    history: Optional[List[MessageHistory]] = []

class AskResponse(BaseModel):
    answer: str
    category: str
    response_time: str