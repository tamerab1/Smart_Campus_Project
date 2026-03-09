from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class ExamSchedule(Base):
    """
    Model representing the exam schedules in the campus.
    """
    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, index=True, nullable=False)
    exam_date = Column(DateTime, nullable=False)
    room_number = Column(String, nullable=False)

class Facility(Base):
    """
    Model representing campus facilities (e.g., library, wifi, study rooms).
    """
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="Active")

class StaffMember(Base):
    __tablename__ = "staff_members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)  # e.g., "Python Lecturer"
    office_location = Column(String)
    office_hours = Column(String)
    email = Column(String)