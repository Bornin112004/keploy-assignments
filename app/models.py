from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    submissions = relationship("Submission", back_populates="student", cascade="all, delete")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime, nullable=False)
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    student = relationship("Student", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
    __table_args__ = (UniqueConstraint('student_id', 'assignment_id', name='_student_assignment_uc'),)