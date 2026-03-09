# app/routes/ask_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ask_schema import AskRequest, AskResponse
from app.database import get_db
from app.models.campus import ExamSchedule
from app.services.ai_service import generate_campus_response
import time

router = APIRouter()

def classify_question(question: str) -> str:
    question_lower = question.lower()
    if "exam" in question_lower or "schedule" in question_lower or "when" in question_lower:
        return "Schedule"
    elif "wifi" in question_lower or "broken" in question_lower or "down" in question_lower:
        return "Technical Issue"
    elif "where" in question_lower or "library" in question_lower:
        return "General Info"
    else:
        return "Out of Scope"

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    category = classify_question(request.question)
    
    if category == "Out of Scope":
        # Mandatory Fallback [cite: 36, 37]
        answer = "I am the Smart Campus Assistant. I can only help with campus schedules, services, and technical issues."
        
    elif category == "Schedule":
        question_lower = request.question.lower()
        if "sql" in question_lower:
            exam = db.query(ExamSchedule).filter(ExamSchedule.course_name.ilike("%sql%")).first()
        elif "python" in question_lower:
            exam = db.query(ExamSchedule).filter(ExamSchedule.course_name.ilike("%python%")).first()
        else:
            exam = None
            
        if exam:
            # Build the context string from the DB record
            formatted_date = exam.exam_date.strftime("%b %d at %H:%M")
            db_context = f"Exam for Course: {exam.course_name}, Date: {formatted_date}, Room: {exam.room_number}"
            
            # Send context and question to Gemini [cite: 29]
            answer = await generate_campus_response(request.question, db_context)
        else:
            answer = "I couldn't find an exam for that course in our system. Please double-check the course name."
            
    else:
        answer = f"This is a placeholder answer for a {category} question. Logic will be added soon."
        
    end_time = time.time()
    calc_time = f"{round(end_time - start_time, 2)}s"
    
    return AskResponse(
        answer=answer,
        category=category,
        response_time=calc_time
    )