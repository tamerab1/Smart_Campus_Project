from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.ask_schema import AskRequest, AskResponse
from app.database import get_db
from app.models.campus import ExamSchedule, Facility, StaffMember, FAQ
from app.services.ai_service import generate_campus_response, model
from google.api_core import exceptions as google_exceptions
import time

router = APIRouter()

async def smart_classify_question(question: str, history: list) -> str:
    history_text = "\n".join([f"{h.role}: {h.content}" for h in history[-2:]])
    
    prompt = f"""You are a classifier. Your ONLY job is to categorize the following user question into one of these:
    'Schedule', 'Technical Issue', 'Staff Info', 'General Info', 'Out of Scope'.
    
    Use the history if the user refers to a previous topic.
    History:
    {history_text}
    
    Question: {question}
    
    Respond with ONLY the category name. Do not explain, do not answer the question, do not include punctuation."""
    
    response = model.generate_content(prompt)
    return response.text.strip()

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    answer = "I'm not sure how to help with that." 
    calc_time = "0s"

    try:
        start_time = time.time()
        category = await smart_classify_question(request.question, request.history)

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
                answer = await generate_campus_response(request.question, db_context, request.history)
            else:
                answer = "I couldn't find an exam for that course in our system."
                
        elif category == "Technical Issue":
            facility = db.query(Facility).filter(Facility.name.ilike("%wi-fi%")).first()
                
            if facility:
                db_context = f"Facility Name: {facility.name}, Location: {facility.location}, Current Status: {facility.status}"
                answer = await generate_campus_response(request.question, db_context, request.history)
            else:
                answer = "I couldn't find information about that technical issue."

        elif category == "Staff Info":
            target_role = None
            q_lower = request.question.lower()
            history_text = " ".join([h.content.lower() for h in request.history[-2:]])
            
            if "python" in q_lower or "python" in history_text:
                target_role = "python"
            elif "sql" in q_lower or "sql" in history_text:
                target_role = "sql"
                
            staff = None
            if target_role:
                staff = db.query(StaffMember).filter(StaffMember.role.ilike(f"%{target_role}%")).first()
                
            if staff:
                db_context = f"Staff Name: {staff.name}, Role: {staff.role}, Office: {staff.office_location}, Office Hours: {staff.office_hours}, Email: {staff.email}"
                answer = await generate_campus_response(request.question, db_context, request.history)
            else:
                answer = "I couldn't find the professor you are referring to."
                
        elif category == "General Info":
            facility = None
            if "205" in request.question:
                facility = db.query(Facility).filter(Facility.name.ilike("%205%")).first()
            elif "102" in request.question:
                facility = db.query(Facility).filter(Facility.name.ilike("%102%")).first()
                
            if facility:
                db_context = f"Facility Name: {facility.name}, Location: {facility.location}"
                answer = await generate_campus_response(request.question, db_context, request.history)
            else:
                faq_match = db.query(FAQ).filter(FAQ.question_topic.ilike(f"%{request.question}%")).first()
                if faq_match:
                    db_context = f"Information: {faq_match.answer_text}"
                    answer = await generate_campus_response(request.question, db_context, request.history)
                else:
                    answer = "I couldn't find that location or general information on campus."
            
        end_time = time.time()
        calc_time = f"{round(end_time - start_time, 2)}s"

        return AskResponse(
            answer=answer,
            category=category,
            response_time=calc_time
        )

    except google_exceptions.ResourceExhausted:
        return AskResponse(
            answer="I am currently a bit overwhelmed! The campus servers are busy. Please try again in a few moments.",
            category="System",
            response_time="0s"
        )
    except Exception as e:
        return AskResponse(
            answer="Something went wrong on my side. Please try again later!",
            category="Error",
            response_time="0s"
        )