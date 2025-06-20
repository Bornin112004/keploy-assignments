from sqlalchemy.orm import Session
from . import models, schemas

def create_assignment(db: Session, assignment: schemas.AssignmentCreate):
    db_assignment = models.Assignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_students_completed(db: Session, assignment_id: int):
    return db.query(models.Student).join(models.Submission).filter(models.Submission.assignment_id == assignment_id).all()

def get_students_pending(db: Session, assignment_id: int):
    submitted = db.query(models.Submission.student_id).filter(models.Submission.assignment_id == assignment_id)
    return db.query(models.Student).filter(~models.Student.id.in_(submitted)).all()

def update_student(db: Session, student_id: int, student_update: schemas.StudentUpdate):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if student:
        for var, value in vars(student_update).items():
            if value is not None:
                setattr(student, var, value)
        db.commit()
        db.refresh(student)
    return student

def delete_assignment(db: Session, assignment_id: int):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if assignment:
        db.delete(assignment)
        db.commit()
    return assignment

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = db.query(models.Student).filter(models.Student.email == student.email).first()
    if db_student:
        return None  # Email already exists
    new_student = models.Student(name=student.name, email=student.email)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

def get_all_students(db: Session):
    return db.query(models.Student).all()

def get_all_assignments(db: Session):
    return db.query(models.Assignment).all()

def get_all_submissions(db: Session):
    return db.query(models.Submission).all()

def create_submission(db: Session, student_id: int, assignment_id: int):
    existing = db.query(models.Submission).filter_by(student_id=student_id, assignment_id=assignment_id).first()
    if existing:
        return existing
    submission = models.Submission(student_id=student_id, assignment_id=assignment_id)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission

def delete_submission(db: Session, student_id: int, assignment_id: int):
    submission = db.query(models.Submission).filter_by(student_id=student_id, assignment_id=assignment_id).first()
    if submission:
        db.delete(submission)
        db.commit()
    return submission