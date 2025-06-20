from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from . import models, schemas, crud
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/assignments/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    return crud.create_assignment(db, assignment)

@app.get("/students/completed/{assignment_id}", response_model=list[schemas.Student])
def students_completed(assignment_id: int, db: Session = Depends(get_db)):
    return crud.get_students_completed(db, assignment_id)

@app.get("/students/pending/{assignment_id}", response_model=list[schemas.Student])
def students_pending(assignment_id: int, db: Session = Depends(get_db)):
    return crud.get_students_pending(db, assignment_id)

@app.put("/students/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id, student)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = crud.delete_assignment(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"ok": True}

@app.post("/students/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    db_student = crud.create_student(db, student)
    if db_student is None:
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_student

@app.get("/students/", response_model=list[schemas.Student])
def list_students(db: Session = Depends(get_db)):
    return crud.get_all_students(db)

@app.get("/assignments/", response_model=list[schemas.Assignment])
def list_assignments(db: Session = Depends(get_db)):
    return crud.get_all_assignments(db)

@app.get("/submissions/", response_model=list[schemas.Submission])
def list_submissions(db: Session = Depends(get_db)):
    return crud.get_all_submissions(db)

@app.post("/submissions/")
def create_submission(student_id: int, assignment_id: int, db: Session = Depends(get_db)):
    return crud.create_submission(db, student_id, assignment_id)

@app.delete("/submissions/")
def delete_submission(student_id: int, assignment_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_submission(db, student_id, assignment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"ok": True}