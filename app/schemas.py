from pydantic import BaseModel, EmailStr
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: EmailStr

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

class Student(StudentBase):
    id: int
    class Config:
        orm_mode = True

class AssignmentBase(BaseModel):
    title: str
    description: str
    due_date: datetime

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int
    class Config:
        orm_mode = True

class Submission(BaseModel):
    id: int
    student_id: int
    assignment_id: int
    submitted_at: datetime
    class Config:
        orm_mode = True