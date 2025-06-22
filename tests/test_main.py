import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    # Create tables before tests
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_student(client):
    # Create student
    resp = client.post("/students/", json={"name": "Integration User", "email": "integration@example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Integration User"
    assert data["email"] == "integration@example.com"
    # Get all students
    resp = client.get("/students/")
    assert resp.status_code == 200
    students = resp.json()
    assert any(s["email"] == "integration@example.com" for s in students)

def test_create_and_get_assignment(client):
    resp = client.post("/assignments/", json={
        "title": "Integration Assignment",
        "description": "Desc",
        "due_date": "2025-07-01T12:00:00"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Integration Assignment"
    # Get all assignments
    resp = client.get("/assignments/")
    assert resp.status_code == 200
    assignments = resp.json()
    assert any(a["title"] == "Integration Assignment" for a in assignments)

def test_submission_crud(client):
    # Create student and assignment
    student = client.post("/students/", json={"name": "Sub User", "email": "sub@example.com"}).json()
    assignment = client.post("/assignments/", json={
        "title": "Sub Assignment",
        "description": "Desc",
        "due_date": "2025-07-02T12:00:00"
    }).json()
    # Create submission
    resp = client.post(f"/submissions/?student_id={student['id']}&assignment_id={assignment['id']}")
    assert resp.status_code == 200
    # Get all submissions
    resp = client.get("/submissions/")
    assert resp.status_code == 200
    submissions = resp.json()
    assert any(
        s["student_id"] == student["id"] and s["assignment_id"] == assignment["id"]
        for s in submissions
    )
    # Delete submission
    resp = client.delete(f"/submissions/?student_id={student['id']}&assignment_id={assignment['id']}")
    assert resp.status_code == 200
    # Confirm deletion
    resp = client.get("/submissions/")
    assert resp.status_code == 200
    submissions = resp.json()
    assert not any(
        s["student_id"] == student["id"] and s["assignment_id"] == assignment["id"]
        for s in submissions
    )

def test_students_completed_and_pending(client):
    # Create students and assignment
    s1 = client.post("/students/", json={"name": "Comp1", "email": "comp1@example.com"}).json()
    s2 = client.post("/students/", json={"name": "Comp2", "email": "comp2@example.com"}).json()
    a = client.post("/assignments/", json={
        "title": "Comp Assignment",
        "description": "Desc",
        "due_date": "2025-07-03T12:00:00"
    }).json()
    # s1 submits, s2 does not
    client.post(f"/submissions/?student_id={s1['id']}&assignment_id={a['id']}")
    # Completed
    resp = client.get(f"/students/completed/{a['id']}")
    assert resp.status_code == 200
    completed = resp.json()
    assert any(stu["id"] == s1["id"] for stu in completed)
    # Pending
    resp = client.get(f"/students/pending/{a['id']}")
    assert resp.status_code == 200
    pending = resp.json()
    assert any(stu["id"] == s2["id"] for stu in pending)

def test_update_student(client):
    # Create a student
    resp = client.post("/students/", json={"name": "ToUpdate", "email": "update@example.com"})
    assert resp.status_code == 200
    student = resp.json()
    # Update the student
    resp = client.put(f"/students/{student['id']}", json={"name": "Updated", "email": "updated@example.com"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["name"] == "Updated"
    assert updated["email"] == "updated@example.com"

def test_delete_assignment(client):
    # Create an assignment
    resp = client.post("/assignments/", json={
        "title": "ToDelete",
        "description": "Desc",
        "due_date": "2025-07-10T12:00:00"
    })
    assert resp.status_code == 200
    assignment = resp.json()
    # Delete the assignment
    resp = client.delete(f"/assignments/{assignment['id']}")
    assert resp.status_code == 200
    # Confirm deletion by listing assignments
    resp = client.get("/assignments/")
    assert resp.status_code == 200
    assignments = resp.json()
    assert not any(a["id"] == assignment["id"] for a in assignments)

def test_create_student_duplicate_email_error(client):
    # Create a student
    resp = client.post("/students/", json={"name": "Dup", "email": "dup@example.com"})
    assert resp.status_code == 200
    # Try to create again with same email
    resp = client.post("/students/", json={"name": "Dup2", "email": "dup@example.com"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"

def test_delete_nonexistent_assignment(client):
    resp = client.delete("/assignments/99999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Assignment not found"