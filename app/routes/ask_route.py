# app/routes/ask_route.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ask_schema import AskRequest, AskResponse
from app.database import get_db
from app.models.campus import ExamSchedule, Facility, StaffMember
from app.services.ai_service import generate_campus_response
import time

router = APIRouter()

def classify_question(question: str) -> str:
    question_lower = question.lower()
    
    # 1. First priority: Check for Staff/Lecturer specific keywords
    if "professor" in question_lower or "lecturer" in question_lower or "office hours" in question_lower or "email" in question_lower:
        return "Staff Info"
        
    # 2. Second priority: Check for Exams and Schedules
    elif "exam" in question_lower or "schedule" in question_lower or "when" in question_lower:
        return "Schedule"
        
    # 3. Third priority: Technical Issues
    elif "wifi" in question_lower or "broken" in question_lower or "down" in question_lower or "work" in question_lower:
        return "Technical Issue"
        
    # 4. Fourth priority: General Info (Rooms, locations)
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
    
    elif category == "Staff Info":
        question_lower = request.question.lower()
        
        if "python" in question_lower:
            staff = db.query(StaffMember).filter(StaffMember.role.ilike("%python%")).first()
        elif "sql" in question_lower:
            staff = db.query(StaffMember).filter(StaffMember.role.ilike("%sql%")).first()
        else:
            staff = None
            
        if staff:
            db_context = f"Staff Name: {staff.name}, Role: {staff.role}, Office: {staff.office_location}, Office Hours: {staff.office_hours}, Email: {staff.email}"
            answer = await generate_campus_response(request.question, db_context)
        else:
            answer = "I couldn't find information for that staff member. Please specify if you are looking for the Python or SQL lecturer."
            
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