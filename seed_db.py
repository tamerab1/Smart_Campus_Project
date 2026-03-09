from datetime import datetime
from app.database import SessionLocal
from app.models.campus import ExamSchedule, Facility

def seed_data():
    db = SessionLocal()
    
    # Check if data already exists to prevent duplication
    if db.query(ExamSchedule).first():
        print("Database already contains data. Skipping seed.")
        db.close()
        return

    print("Seeding database with mock data...")

    # Add Exam Schedules (Based on UC-01)
    exams = [
        ExamSchedule(course_name="SQL", exam_date=datetime(2026, 2, 25, 9, 0), room_number="401"),
        ExamSchedule(course_name="Python", exam_date=datetime(2026, 3, 15, 14, 0), room_number="302"),
        ExamSchedule(course_name="Data Structures", exam_date=datetime(2026, 3, 20, 10, 0), room_number="105")
    ]
    db.add_all(exams)

    # Add Facilities (Based on UC-02, UC-03, UC-04)
    facilities = [
        Facility(name="Main Library", location="Building 4, 2nd floor", status="Active"),
        Facility(name="Library Wi-Fi", location="Main Library", status="Down"),
        Facility(name="Room 205", location="Floor 2, next to coffee station", status="Active"),
        Facility(name="Room 102", location="Floor 1, above cafeteria", status="Active")
    ]
    db.add_all(facilities)

    # Save to database
    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()