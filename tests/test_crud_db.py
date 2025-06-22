import pytest
from app import crud, schemas, models
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Use a separate test database (SQLite in-memory for isolation)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_student(db):
    student = schemas.StudentCreate(name="Real User", email="real@example.com")
    created = crud.create_student(db, student)
    assert created is not None, "Student creation failed"
    assert getattr(created, "name", None) == "Real User"
    assert getattr(created, "email", None) == "real@example.com"
    students = crud.get_all_students(db)
    assert any(s.email == "real@example.com" for s in students)

def test_create_assignment_and_delete(db):
    assignment = schemas.AssignmentCreate(title="T", description="D", due_date=datetime.fromisoformat("2025-06-30T23:59:00"))
    created = crud.create_assignment(db, assignment)
    assert getattr(created, "title", None) == "T"
    deleted = crud.delete_assignment(db, getattr(created, "id"))
    assert deleted is not None, "Assignment was not deleted or not found"
    assert getattr(deleted, "id", None) == getattr(created, "id", None)

def test_get_students_completed_and_pending(db):
    # Setup: create students, assignment, and submission
    s1 = crud.create_student(db, schemas.StudentCreate(name="S1", email="s1@x.com"))
    db.flush()
    s2 = crud.create_student(db, schemas.StudentCreate(name="S2", email="s2@x.com"))
    db.flush()
    a1 = crud.create_assignment(db, schemas.AssignmentCreate(title="A1", description="D", due_date=datetime.fromisoformat("2025-06-30T23:59:00")))
    db.flush()
    assert s1 is not None and getattr(s1, "id", None) is not None, "s1 or s1.id is None"
    assert s2 is not None and getattr(s2, "id", None) is not None, "s2 or s2.id is None"
    assert a1 is not None and getattr(a1, "id", None) is not None, "a1 or a1.id is None"
    crud.create_submission(db, getattr(s1, "id"), getattr(a1, "id"))
    completed = crud.get_students_completed(db, getattr(a1, "id"))
    pending = crud.get_students_pending(db, getattr(a1, "id"))
    assert any(s.id == s1.id for s in completed)
    assert all(s.id != s1.id for s in pending)
    assert any(s.id == s2.id for s in pending)

def test_get_all_students_assignments_submissions(db):
    s = crud.create_student(db, schemas.StudentCreate(name="S", email="s@x.com"))
    a = crud.create_assignment(db, schemas.AssignmentCreate(title="A", description="D", due_date=datetime.fromisoformat("2025-06-30T23:59:00")))
    db.flush()
    assert s is not None and getattr(s, "id", None) is not None, "Student creation failed or id is None"
    assert a is not None and getattr(a, "id", None) is not None, "Assignment creation failed or id is None"
    sub = crud.create_submission(db, getattr(s, "id"), getattr(a, "id"))
    students = crud.get_all_students(db)
    assignments = crud.get_all_assignments(db)
    submissions = crud.get_all_submissions(db)
    assert any(st.id == s.id for st in students)
    assert any(asg.id == a.id for asg in assignments)
    a = crud.create_assignment(db, schemas.AssignmentCreate(title="A3", description="D", due_date=datetime.fromisoformat("2025-06-30T23:59:00")))
    a = crud.create_assignment(db, schemas.AssignmentCreate(title="A3", description="D", due_date=datetime.fromisoformat("2025-06-30T23:59:00")))
    db.flush()
    assert s is not None and getattr(s, "id", None) is not None, "Student creation failed or id is None"
    assert a is not None and getattr(a, "id", None) is not None, "Assignment creation failed or id is None"
    sub = crud.create_submission(db, getattr(s, "id"), getattr(a, "id"))
    assert getattr(sub, "student_id", None) == getattr(s, "id", None)
    deleted = crud.delete_submission(db, getattr(s, "id"), getattr(a, "id"))
    assert deleted is not None
    # Should not find submission after delete
    assert crud.delete_submission(db, getattr(s, "id"), getattr(a, "id")) is None
    assert deleted is not None
    # Should not find submission after delete
    assert crud.delete_submission(db, getattr(s, "id"), getattr(a, "id")) is None