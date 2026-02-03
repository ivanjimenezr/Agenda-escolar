"""
Integration tests for Subject API endpoints

These tests specifically test Pydantic serialization of SQLAlchemy models
and subject CRUD operations to catch issues before deployment.
"""

import pytest
from datetime import time, timedelta, date
from fastapi.testclient import TestClient

from src.main import app
from src.domain.models import User, StudentProfile, Subject
from src.application.schemas.subject import SubjectResponse


@pytest.fixture
def auth_headers(client: TestClient, db_session):
    """Create a user and return authentication headers"""
    from src.infrastructure.security.password import hash_password
    from src.infrastructure.security.jwt import create_access_token

    # Create user
    user = User(
        email="testsubject@example.com",
        name="Test Subject User",
        password_hash=hash_password("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Create access token
    token = create_access_token({"sub": str(user.id)})

    return {"Authorization": f"Bearer {token}"}, user


@pytest.fixture
def sample_student(db_session, auth_headers):
    """Create a sample student profile"""
    headers, user = auth_headers

    student = StudentProfile(
        user_id=user.id,
        name="Test Student Subject",
        school="Test School",
        grade="5th Grade",
        allergies=[],
        excluded_foods=[]
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    return student


class TestSubjectEndpointsSerialization:
    """Test suite specifically for Subject Pydantic serialization issues"""

    def test_create_subject_and_serialize(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test creating a subject and serializing the response"""
        headers, user = auth_headers

        payload = {
            "name": "Matemáticas",
            "days": ["Lunes", "Miércoles", "Viernes"],
            "time": "09:00:00",
            "teacher": "Prof. García",
            "color": "#FF5733",
            "type": "colegio"
        }

        response = client.post(
            f"/students/{sample_student.id}/subjects",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()

        # Verify all fields are present
        assert "id" in data
        assert data["student_id"] == str(sample_student.id)
        assert data["name"] == "Matemáticas"
        assert data["days"] == ["Lunes", "Miércoles", "Viernes"]
        assert data["teacher"] == "Prof. García"
        assert data["color"] == "#FF5733"
        assert data["type"] == "colegio"

        # This line will trigger RecursionError if relationships are loaded
        assert "student" not in data  # Should not include relationship

    def test_get_student_subjects_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test getting multiple subjects - this is where RecursionError typically occurs"""
        headers, user = auth_headers

        # Create multiple subjects
        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        subject1 = repo.create(
            student_id=sample_student.id,
            name="Matemáticas",
            days=["Lunes", "Miércoles"],
            time=time(9, 0),
            teacher="Prof. García",
            color="#FF5733",
            type="colegio"
        )

        subject2 = repo.create(
            student_id=sample_student.id,
            name="Lengua",
            days=["Martes", "Jueves"],
            time=time(10, 30),
            teacher="Prof. Martínez",
            color="#33FF57",
            type="colegio"
        )

        subject3 = repo.create(
            student_id=sample_student.id,
            name="Fútbol",
            days=["Viernes"],
            time=time(16, 0),
            teacher="Entrenador López",
            color="#3357FF",
            type="extraescolar"
        )

        # THIS IS THE CRITICAL TEST - Getting multiple subjects
        response = client.get(
            f"/students/{sample_student.id}/subjects",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Verify each subject is properly serialized
        for subject_item in data:
            assert "id" in subject_item
            assert "student_id" in subject_item
            assert "name" in subject_item
            assert "days" in subject_item
            assert "time" in subject_item
            assert "teacher" in subject_item
            assert "color" in subject_item
            assert "type" in subject_item
            # Should NOT include relationship fields
            assert "student" not in subject_item

    def test_pydantic_model_validate_subject_directly(self, db_session, sample_student):
        """Test Pydantic model_validate directly with Subject SQLAlchemy model"""
        from src.infrastructure.repositories.subject_repository import SubjectRepository

        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Test Subject",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Test Teacher",
            color="#FFFFFF",
            type="colegio"
        )

        # This is what happens in the endpoint - THIS SHOULD NOT CAUSE RecursionError
        try:
            response_model = SubjectResponse.model_validate(subject)
            assert response_model.id == subject.id
            assert response_model.name == "Test Subject"
            assert response_model.student_id == sample_student.id
            assert response_model.days == ["Lunes"]
            assert response_model.type == "colegio"
        except RecursionError as e:
            pytest.fail(f"RecursionError occurred during Pydantic serialization: {e}")

    def test_update_subject_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test updating a subject and serializing response"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Original Name",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Original Teacher",
            color="#FF0000",
            type="colegio"
        )

        update_payload = {
            "name": "Updated Name",
            "teacher": "Updated Teacher",
            "color": "#00FF00"
        }

        response = client.put(
            f"/students/{sample_student.id}/subjects/{subject.id}",
            json=update_payload,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["name"] == "Updated Name"
        assert data["teacher"] == "Updated Teacher"
        assert data["color"] == "#00FF00"
        # Unchanged fields
        assert data["days"] == ["Lunes"]
        assert data["type"] == "colegio"
        assert "student" not in data

    def test_update_subject_with_time_string(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test updating subject with time as string (frontend sends strings)"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Test Subject",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Test Teacher",
            color="#FF0000",
            type="colegio"
        )

        # Update with time as string
        update_payload = {
            "time": "14:30:00"
        }

        response = client.put(
            f"/students/{sample_student.id}/subjects/{subject.id}",
            json=update_payload,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        # Time should be parsed and returned
        assert "14:30" in data["time"]
        assert "student" not in data

    def test_create_multiple_subjects_different_times(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test creating multiple subjects at different times"""
        headers, user = auth_headers

        subjects_data = [
            {
                "name": "Matemáticas",
                "days": ["Lunes"],
                "time": "09:00:00",
                "teacher": "Prof. A",
                "color": "#FF0000",
                "type": "colegio"
            },
            {
                "name": "Lengua",
                "days": ["Lunes"],
                "time": "10:00:00",
                "teacher": "Prof. B",
                "color": "#00FF00",
                "type": "colegio"
            },
            {
                "name": "Inglés",
                "days": ["Martes"],
                "time": "09:00:00",
                "teacher": "Prof. C",
                "color": "#0000FF",
                "type": "colegio"
            }
        ]

        created_ids = []
        for subject_data in subjects_data:
            response = client.post(
                f"/students/{sample_student.id}/subjects",
                json=subject_data,
                headers=headers
            )
            assert response.status_code == 201
            data = response.json()
            created_ids.append(data["id"])
            assert "student" not in data

        # Get all subjects
        response = client.get(
            f"/students/{sample_student.id}/subjects",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # Verify no recursion errors
        for item in data:
            assert "student" not in item

    def test_get_single_subject_by_id(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test getting a single subject by ID"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="Single Subject Test",
            days=["Miércoles"],
            time=time(11, 0),
            teacher="Test Teacher",
            color="#ABCDEF",
            type="extraescolar"
        )

        response = client.get(
            f"/students/{sample_student.id}/subjects/{subject.id}",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(subject.id)
        assert data["name"] == "Single Subject Test"
        assert "student" not in data

    def test_delete_subject_serialization(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test deleting a subject"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        subject = repo.create(
            student_id=sample_student.id,
            name="To Delete",
            days=["Jueves"],
            time=time(12, 0),
            teacher="Test Teacher",
            color="#123456",
            type="colegio"
        )

        # Delete
        response = client.delete(
            f"/students/{sample_student.id}/subjects/{subject.id}",
            headers=headers
        )

        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(
            f"/students/{sample_student.id}/subjects/{subject.id}",
            headers=headers
        )
        assert response.status_code == 404

    def test_create_subject_with_conflict_without_replace(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test creating conflicting subject without replace flag"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        # Create first subject
        repo.create(
            student_id=sample_student.id,
            name="Existing Subject",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Teacher A",
            color="#FF0000",
            type="colegio"
        )

        # Try to create conflicting subject (same day and time)
        payload = {
            "name": "Conflicting Subject",
            "days": ["Lunes"],
            "time": "09:00:00",
            "teacher": "Teacher B",
            "color": "#00FF00",
            "type": "colegio"
        }

        response = client.post(
            f"/students/{sample_student.id}/subjects",
            json=payload,
            headers=headers
        )

        # Should return conflict error
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data

    def test_create_subject_with_replace_flag(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test creating subject with replace=True for conflicts"""
        headers, user = auth_headers

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        # Create first subject
        old_subject = repo.create(
            student_id=sample_student.id,
            name="Old Subject",
            days=["Martes"],
            time=time(10, 0),
            teacher="Old Teacher",
            color="#FF0000",
            type="colegio"
        )

        # Create with replace=True
        payload = {
            "name": "New Subject",
            "days": ["Martes"],
            "time": "10:00:00",
            "teacher": "New Teacher",
            "color": "#00FF00",
            "type": "colegio"
        }

        response = client.post(
            f"/students/{sample_student.id}/subjects?replace=true",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Subject"
        assert "student" not in data

        # Old subject should be soft-deleted
        all_subjects = client.get(
            f"/students/{sample_student.id}/subjects",
            headers=headers
        )
        subjects_list = all_subjects.json()
        # Should only have the new one
        assert len(subjects_list) == 1
        assert subjects_list[0]["name"] == "New Subject"

    def test_subject_type_case_insensitive(self, client: TestClient, auth_headers, sample_student, db_session):
        """Test that subject type is case insensitive"""
        headers, user = auth_headers

        payload = {
            "name": "Test Subject",
            "days": ["Viernes"],
            "time": "15:00:00",
            "teacher": "Test",
            "color": "#AABBCC",
            "type": "COLEGIO"  # Uppercase
        }

        response = client.post(
            f"/students/{sample_student.id}/subjects",
            json=payload,
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        # Should be normalized to lowercase
        assert data["type"] == "colegio"

    def test_multiple_students_no_subject_recursion(self, client: TestClient, auth_headers, db_session):
        """Test with multiple students to ensure no cross-contamination"""
        headers, user = auth_headers

        # Create multiple students
        student1 = StudentProfile(
            user_id=user.id,
            name="Student 1",
            school="School 1",
            grade="5th"
        )
        student2 = StudentProfile(
            user_id=user.id,
            name="Student 2",
            school="School 2",
            grade="6th"
        )
        db_session.add_all([student1, student2])
        db_session.commit()
        db_session.refresh(student1)
        db_session.refresh(student2)

        from src.infrastructure.repositories.subject_repository import SubjectRepository
        repo = SubjectRepository(db_session)

        # Create subjects for each student
        for student in [student1, student2]:
            for i in range(3):
                repo.create(
                    student_id=student.id,
                    name=f"Subject {i}",
                    days=["Lunes"],
                    time=time(9 + i, 0),
                    teacher=f"Teacher {i}",
                    color="#FF0000",
                    type="colegio"
                )

        # Get subjects for student1
        response1 = client.get(f"/students/{student1.id}/subjects", headers=headers)
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1) == 3

        # Get subjects for student2
        response2 = client.get(f"/students/{student2.id}/subjects", headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 3

        # Verify no recursion errors occurred
        for item in data1 + data2:
            assert "student" not in item
