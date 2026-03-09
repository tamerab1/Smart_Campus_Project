# seed_db.py
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.campus import ExamSchedule, Facility, StaffMember
from datetime import datetime

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def seed_data():
    db: Session = SessionLocal()
    
    try:
        # Clear existing data to avoid duplicates on multiple runs
        db.query(ExamSchedule).delete()
        db.query(Facility).delete()
        db.query(StaffMember).delete()
        
        # 1. Seed Exams
        exam1 = ExamSchedule(course_name="Introduction to Python", exam_date=datetime(2026, 2, 20, 14, 0), room_number="101")
        exam2 = ExamSchedule(course_name="Advanced SQL", exam_date=datetime(2026, 2, 25, 9, 0), room_number="401")
        db.add_all([exam1, exam2])
        
        # 2. Seed Facilities
        fac1 = Facility(name="Main Library Wi-Fi", location="Library Building", status="Down")
        fac2 = Facility(name="Room 205", location="Floor 2, next to coffee station", status="Active")
        fac3 = Facility(name="Room 102", location="Floor 1, near main entrance", status="Active")
        db.add_all([fac1, fac2, fac3])

        # 3. Seed Staff Members
        staff1 = StaffMember(
            name="Dr. Alice Smith", 
            role="Python Lecturer", 
            office_location="Building B, Room 301", 
            office_hours="Mon & Wed 10:00-12:00", 
            email="alice@smartcampus.edu"
        )
        staff2 = StaffMember(
            name="Prof. Bob Jones", 
            role="SQL Lecturer", 
            office_location="Building A, Room 405", 
            office_hours="Tue & Thu 14:00-16:00", 
            email="bob@smartcampus.edu"
        )
        db.add_all([staff1, staff2])
        
        db.commit()
        print("Database seeded successfully with Exams, Facilities, and Staff!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()