from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
import time
import traceback

from app.schemas.ask_schema import AskRequest, AskResponse
from app.core.database import get_db
from app.models.campus import ExamSchedule, Facility, StaffMember, FAQ
from app.services.ai_service import get_ai_category_and_answer

router = APIRouter()

# שליפה מרוכזת כדי לחסוך פניות מיותרות ל-DB
def fetch_all_data(db: Session):
    return {
        "exams": db.query(ExamSchedule).all(),
        "facilities": db.query(Facility).all(),
        "staff": db.query(StaffMember).all(),
        "faqs": db.query(FAQ).all()
    }

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    try:
        start_time = time.time()
        
        # 1. שליפה אסינכרונית כדי לא לתקוע את השרת
        data = await run_in_threadpool(fetch_all_data, db)
        
        # 2. בניית קונטקסט נקי, שורות-שורות (הרבה יותר קריא ל-AI מאשר פסיקים)
        db_context = f"""
        --- EXAMS ---
        {"\n".join([f"Course: {e.course_name}, Date: {e.exam_date.strftime('%b %d')}" for e in data['exams']])}
        
        --- FACILITIES (Wi-Fi, Labs) ---
        {"\n".join([f"Name: {f.name}, Location: {f.location}, Status: {f.status}" for f in data['facilities']])}
        
        --- STAFF DIRECTORY ---
        {"\n".join([f"Name: {s.name}, Email: {s.email}, Role: {s.role}" for s in data['staff']])}
        
        --- FAQS ---
        {"\n".join([f"Q: {faq.question_topic}, A: {faq.answer_text}" for faq in data['faqs']])}
        """
        
        # 3. קריאה משולבת ל-AI (סיווג + תשובה)
        category, answer = await get_ai_category_and_answer(request.question, db_context, request.history)
                
        return AskResponse(
            answer=answer,
            category=category,
            response_time=f"{round(time.time() - start_time, 2)}s"
        )

    except Exception as e:
        # הדפסת השגיאה המלאה לטרמינל לדיבוג מהיר
        traceback.print_exc()
        return AskResponse(
            answer="Something went wrong, please check the server logs.", 
            category="Error", 
            response_time="0s"
        )