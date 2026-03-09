from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    # Validating that the question is at least 3 characters long
    question: str = Field(..., min_length=3, description="The student's campus-related query")

class AskResponse(BaseModel):
    answer: str
    category: str
    response_time: str = None