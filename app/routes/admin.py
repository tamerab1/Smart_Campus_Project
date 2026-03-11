from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.auth import verify_admin
from app.core.database import get_db
from app.models.campus import FAQ, StaffMember, Facility, ExamSchedule

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", dependencies=[Depends(verify_admin)], response_class=HTMLResponse)
async def admin_dashboard(request: Request, table: str = "faq", db: Session = Depends(get_db)):
   
    data = []
    if table == "faq":
        data = db.query(FAQ).all()
    elif table == "staff":
        data = db.query(StaffMember).all()
    elif table == "facility":
        data = db.query(Facility).all()
    elif table == "exam":
        data = db.query(ExamSchedule).all()

    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "data": data, 
        "current_table": table
    })

# --- Routes for FAQ ---
@router.post("/faq/add", dependencies=[Depends(verify_admin)])
async def add_faq(category: str = Form(...), question: str = Form(...), answer: str = Form(...), db: Session = Depends(get_db)):
    db.add(FAQ(category=category, question_topic=question, answer_text=answer))
    db.commit()
    return RedirectResponse(url="/admin?table=faq", status_code=303)

@router.post("/faq/delete/{item_id}", dependencies=[Depends(verify_admin)])
async def delete_faq(item_id: int, db: Session = Depends(get_db)):
    db.query(FAQ).filter(FAQ.id == item_id).delete()
    db.commit()
    return RedirectResponse(url="/admin?table=faq", status_code=303)

# --- Routes for Staff Members ---
@router.post("/staff/add", dependencies=[Depends(verify_admin)])
async def add_staff(name: str = Form(...), role: str = Form(...), email: str = Form(...), office_location: str = Form(""), office_hours: str = Form(""), db: Session = Depends(get_db)):
    db.add(StaffMember(name=name, role=role, email=email, office_location=office_location, office_hours=office_hours))
    db.commit()
    return RedirectResponse(url="/admin?table=staff", status_code=303)

@router.post("/staff/delete/{item_id}", dependencies=[Depends(verify_admin)])
async def delete_staff(item_id: int, db: Session = Depends(get_db)):
    db.query(StaffMember).filter(StaffMember.id == item_id).delete()
    db.commit()
    return RedirectResponse(url="/admin?table=staff", status_code=303)

# --- Routes for Facilities ---
@router.post("/facility/add", dependencies=[Depends(verify_admin)])
async def add_facility(name: str = Form(...), location: str = Form(...), status: str = Form("Active"), db: Session = Depends(get_db)):
    db.add(Facility(name=name, location=location, status=status))
    db.commit()
    return RedirectResponse(url="/admin?table=facility", status_code=303)

@router.post("/facility/delete/{item_id}", dependencies=[Depends(verify_admin)])
async def delete_facility(item_id: int, db: Session = Depends(get_db)):
    db.query(Facility).filter(Facility.id == item_id).delete()
    db.commit()
    return RedirectResponse(url="/admin?table=facility", status_code=303)

# --- Routes for Exam Schedules ---
@router.post("/exam/add", dependencies=[Depends(verify_admin)])
async def add_exam(course_name: str = Form(...), exam_date: str = Form(...), room_number: str = Form(...), db: Session = Depends(get_db)):
    # ממיר את התאריך שמגיע מהטופס לאובייקט DateTime
    date_obj = datetime.strptime(exam_date, "%Y-%m-%dT%H:%M")
    db.add(ExamSchedule(course_name=course_name, exam_date=date_obj, room_number=room_number))
    db.commit()
    return RedirectResponse(url="/admin?table=exam", status_code=303)

@router.post("/exam/delete/{item_id}", dependencies=[Depends(verify_admin)])
async def delete_exam(item_id: int, db: Session = Depends(get_db)):
    db.query(ExamSchedule).filter(ExamSchedule.id == item_id).delete()
    db.commit()
    return RedirectResponse(url="/admin?table=exam", status_code=303)

@router.get("/{table}/edit/{item_id}", dependencies=[Depends(verify_admin)], response_class=HTMLResponse)
async def edit_page(table: str, item_id: int, request: Request, db: Session = Depends(get_db)):
    """טוען את הפריט הספציפי מהטבלה הנכונה לצורך עריכה"""
    item = None
    if table == "faq":
        item = db.query(FAQ).filter(FAQ.id == item_id).first()
    elif table == "staff":
        item = db.query(StaffMember).filter(StaffMember.id == item_id).first()
    elif table == "facility":
        item = db.query(Facility).filter(Facility.id == item_id).first()
    elif table == "exam":
        item = db.query(ExamSchedule).filter(ExamSchedule.id == item_id).first()
    
    if not item:
        return RedirectResponse(url=f"/admin?table={table}")
        
    return templates.TemplateResponse("edit.html", {"request": request, "item": item, "current_table": table})

@router.post("/{table}/update/{item_id}", dependencies=[Depends(verify_admin)])
async def update_item(table: str, item_id: int, request: Request, db: Session = Depends(get_db)):
    """מקבל את הטופס ושומר את השינויים במסד הנתונים"""
    form_data = await request.form()
    
    if table == "faq":
        item = db.query(FAQ).filter(FAQ.id == item_id).first()
        if item:
            item.category = form_data.get("category")
            item.question_topic = form_data.get("question")
            item.answer_text = form_data.get("answer")
            
    elif table == "staff":
        item = db.query(StaffMember).filter(StaffMember.id == item_id).first()
        if item:
            item.name = form_data.get("name")
            item.role = form_data.get("role")
            item.email = form_data.get("email")
            item.office_location = form_data.get("office_location")
            item.office_hours = form_data.get("office_hours")
            
    elif table == "facility":
        item = db.query(Facility).filter(Facility.id == item_id).first()
        if item:
            item.name = form_data.get("name")
            item.location = form_data.get("location")
            item.status = form_data.get("status")
            
    elif table == "exam":
        item = db.query(ExamSchedule).filter(ExamSchedule.id == item_id).first()
        if item:
            item.course_name = form_data.get("course_name")
            item.room_number = form_data.get("room_number")
            exam_date_str = form_data.get("exam_date")
            if exam_date_str:
                item.exam_date = datetime.strptime(exam_date_str, "%Y-%m-%dT%H:%M")
    
    db.commit()
    return RedirectResponse(url=f"/admin?table={table}", status_code=303)