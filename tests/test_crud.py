from unittest.mock import MagicMock
from app import crud, schemas, models

def test_create_student_unit():
    db = MagicMock()
    student = schemas.StudentCreate(name="Unit User", email="unit@example.com")
    db.query().filter().first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = crud.create_student(db, student)
    assert result is not None

def test_create_student_duplicate_email():
    db = MagicMock()
    student = schemas.StudentCreate(name="Unit User", email="unit@example.com")
    db.query().filter().first.return_value = models.Student(id=1, name="Unit User", email="unit@example.com")
    result = crud.create_student(db, student)
    assert result is None

def test_update_student_unit():
    db = MagicMock()
    student_obj = models.Student(id=1, name="Old", email="old@example.com")
    db.query().filter().first.return_value = student_obj
    update = schemas.StudentUpdate(name="New", email="new@example.com")
    db.commit = MagicMock()
    db.refresh = MagicMock()
    result = crud.update_student(db, 1, update)
    assert result is not None
    assert getattr(result, "name") == "New"
    assert getattr(result, "email") == "new@example.com"

def test_delete_assignment_unit():
    db = MagicMock()
    assignment_obj = models.Assignment(id=1, title="A", description="D", due_date=None)
    db.query().filter().first.return_value = assignment_obj
    db.delete = MagicMock()
    db.commit = MagicMock()
    result = crud.delete_assignment(db, 1)
    assert result == assignment_obj

def test_delete_assignment_not_found():
    db = MagicMock()
    db.query().filter().first.return_value = None
    result = crud.delete_assignment(db, 1)
    assert result is None

def test_get_students_completed_unit():
    db = MagicMock()
    db.query().join().filter().all.return_value = [models.Student(id=1, name="A", email="a@x.com")]
    result = crud.get_students_completed(db, 1)
    assert isinstance(result, list)
    assert getattr(result[0], "name", None) == "A"

def test_get_students_pending_unit():
    db = MagicMock()
    db.query().filter().all.return_value = [models.Student(id=2, name="B", email="b@x.com")]
    db.query().filter().subquery.return_value = [1]
    result = crud.get_students_pending(db, 1)
    assert isinstance(result, list)
    assert getattr(result[0], "name", None) == "B"

def test_get_all_students_unit():
    db = MagicMock()
    db.query().all.return_value = [models.Student(id=1, name="A", email="a@x.com")]
    result = crud.get_all_students(db)
    assert isinstance(result, list)
    assert getattr(result[0], "name", None) == "A"

def test_get_all_assignments_unit():
    db = MagicMock()
    db.query().all.return_value = [models.Assignment(id=1, title="T", description="D", due_date=None)]
    result = crud.get_all_assignments(db)
    assert isinstance(result, list)
    assert str(result[0].title) == "T"

def test_get_all_submissions_unit():
    db = MagicMock()
    db.query().all.return_value = [models.Submission(id=1, student_id=1, assignment_id=1)]
    result = crud.get_all_submissions(db)
    assert isinstance(result, list)
    assert getattr(result[0], "id", None) == 1

def test_create_submission_unit():
    db = MagicMock()
    db.query().filter_by().first.return_value = None
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db_sub = models.Submission(id=1, student_id=1, assignment_id=1)
    db.refresh.side_effect = lambda x: x
    result = crud.create_submission(db, 1, 1)
    # Since we don't return a real object, just check that add/commit/refresh were called
    db.add.assert_called()
    db.commit.assert_called()
    db.refresh.assert_called()

def test_delete_submission_unit():
    db = MagicMock()
    db_sub = models.Submission(id=1, student_id=1, assignment_id=1)
    db.query().filter_by().first.return_value = db_sub
    db.delete = MagicMock()
    db.commit = MagicMock()
    result = crud.delete_submission(db, 1, 1)
    assert result == db_sub
    db.delete.assert_called_with(db_sub)
    db.commit.assert_called()