"""
Student Profile Repository

Data access layer for StudentProfile entity
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domain.models import StudentProfile


class StudentRepository:
    """Repository for student profile data access"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: UUID,
        name: str,
        school: str,
        grade: str,
        avatar_url: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        excluded_foods: Optional[List[str]] = None
    ) -> StudentProfile:
        """Create a new student profile"""
        student = StudentProfile(
            user_id=user_id,
            name=name,
            school=school,
            grade=grade,
            avatar_url=avatar_url,
            allergies=allergies or [],
            excluded_foods=excluded_foods or []
        )
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

    def get_by_id(self, student_id: UUID) -> Optional[StudentProfile]:
        """Get student profile by ID (excludes soft-deleted)"""
        return self.db.query(StudentProfile).filter(
            StudentProfile.id == student_id,
            StudentProfile.deleted_at.is_(None)
        ).first()

    def get_by_user_id(self, user_id: UUID) -> List[StudentProfile]:
        """Get all student profiles for a user (excludes soft-deleted)"""
        return self.db.query(StudentProfile).filter(
            StudentProfile.user_id == user_id,
            StudentProfile.deleted_at.is_(None)
        ).order_by(StudentProfile.created_at).all()

    def update(
        self,
        student_id: UUID,
        name: Optional[str] = None,
        school: Optional[str] = None,
        grade: Optional[str] = None,
        avatar_url: Optional[str] = None,
        allergies: Optional[List[str]] = None,
        excluded_foods: Optional[List[str]] = None
    ) -> Optional[StudentProfile]:
        """Update student profile"""
        student = self.get_by_id(student_id)
        if not student:
            return None

        if name is not None:
            student.name = name
        if school is not None:
            student.school = school
        if grade is not None:
            student.grade = grade
        if avatar_url is not None:
            student.avatar_url = avatar_url
        if allergies is not None:
            student.allergies = allergies
        if excluded_foods is not None:
            student.excluded_foods = excluded_foods

        student.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(student)
        return student

    def delete(self, student_id: UUID) -> bool:
        """Soft delete a student profile"""
        student = self.get_by_id(student_id)
        if not student:
            return False

        student.deleted_at = datetime.utcnow()
        self.db.commit()
        return True

    def verify_ownership(self, student_id: UUID, user_id: UUID) -> bool:
        """Verify that a student belongs to a specific user"""
        student = self.db.query(StudentProfile).filter(
            StudentProfile.id == student_id,
            StudentProfile.deleted_at.is_(None)
        ).first()

        if not student:
            return False

        return student.user_id == user_id
