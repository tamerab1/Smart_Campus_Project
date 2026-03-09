# app/routes/ask_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ask_schema import AskRequest, AskResponse
from app.database import get_db
from app.models.campus import ExamSchedule, Facility
from app.services.ai_service import generate_campus_response
import time

router = APIRouter()

def classify_question(question: str) -> str:
    question_lower = question.lower()
    if "exam" in question_lower or "schedule" in question_lower or "when" in question_lower:
        return "Schedule"
    elif "wifi" in question_lower or "broken" in question_lower or "down" in question_lower or "work" in question_lower:
        return "Technical Issue"
    elif "where" in question_lower or "library" in question_lower or "room" in question_lower:
        return "General Info"
    else:
        return "Out of Scope"

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    category = classify_question(request.question)
    
    if category == "Out of Scope":
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
            formatted_date = exam.exam_date.strftime("%b %d at %H:%M")
            db_context = f"Exam for Course: {exam.course_name}, Date: {formatted_date}, Room: {exam.room_number}"
            answer = await generate_campus_response(request.question, db_context)
        else:
            answer = "I couldn't find an exam for that course in our system. Please double-check the course name."
            
    elif category == "Technical Issue":
        question_lower = request.question.lower()
        if "wifi" in question_lower or "wi-fi" in question_lower:
            facility = db.query(Facility).filter(Facility.name.ilike("%wi-fi%")).first()
        else:
            facility = None
            
        if facility:
            db_context = f"Facility Name: {facility.name}, Location: {facility.location}, Current Status: {facility.status}"
            answer = await generate_campus_response(request.question, db_context)
        else:
            answer = "I couldn't find information about that specific facility or service."
            
    elif category == "General Info":
        question_lower = request.question.lower()
        
        # Determine which location the user is asking about
        if "library" in question_lower and "wifi" not in question_lower and "wi-fi" not in question_lower:
            facility = db.query(Facility).filter(Facility.name == "Main Library").first()
        elif "205" in question_lower:
            facility = db.query(Facility).filter(Facility.name.ilike("%205%")).first()
        elif "102" in question_lower:
            facility = db.query(Facility).filter(Facility.name.ilike("%102%")).first()
        else:
            facility = None
            
        if facility:
            # Build context with just the location for Gemini
            db_context = f"Facility Name: {facility.name}, Location: {facility.location}"
            answer = await generate_campus_response(request.question, db_context)
        else:
            answer = "I couldn't find the location you're looking for on campus."
            
    else:
        answer = "I am not sure how to help with that."
        
    end_time = time.time()
    calc_time = f"{round(end_time - start_time, 2)}s"
    
    return AskResponse(
        answer=answer,
        category=category,
        response_time=calc_time
    )