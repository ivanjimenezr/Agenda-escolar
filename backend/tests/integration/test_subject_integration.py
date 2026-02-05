import uuid
from datetime import time

# Skip these integration tests if docker is not available
import docker
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _docker_available() -> bool:
    try:
        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


from testcontainers.postgres import PostgresContainer

from src.application.exceptions import ConflictError
from src.domain.models import StudentProfile, SubjectType, User
from src.infrastructure.database import Base
from src.infrastructure.repositories.subject_repository import SubjectRepository


@pytest.mark.integration
@pytest.mark.skipif(not _docker_available(), reason="Docker not available, skipping heavy integration tests")
def test_uppercase_days_normalized_and_conflict_detection():
    """Ensure uppercase enum names in input (e.g., 'LUNES') are normalized
    and do not cause PostgreSQL invalid enum errors. Also verify conflict detection.
    """
    with PostgresContainer("postgres:15-alpine") as pg:
        engine = create_engine(pg.get_connection_url())
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create a user and student
        user = User(email="u@example.com", name="U", password_hash="hash")
        session.add(user)
        session.flush()

        student = StudentProfile(user_id=user.id, name="S", school="X", grade="1")
        session.add(student)
        session.commit()

        repo = SubjectRepository(session)

        # Create initial subject using proper enum value
        subj = repo.create(
            student_id=student.id,
            name="Matemáticas",
            days=["Lunes"],
            time=time(9, 0),
            teacher="Prof",
            color="#112233",
            type=SubjectType.COLEGIO,
        )
        assert subj is not None

        # Attempt to create with uppercase day names -> should be normalized and produce a ConflictError
        with pytest.raises(ConflictError):
            repo.create(
                student_id=student.id,
                name="Matemáticas 2",
                days=["LUNES"],
                time=time(9, 0),
                teacher="Prof",
                color="#112233",
                type=SubjectType.COLEGIO,
            )

        session.close()
        engine.dispose()
        Base.metadata.drop_all(bind=engine)


@pytest.mark.integration
@pytest.mark.skipif(not _docker_available(), reason="Docker not available, skipping heavy integration tests")
def test_replace_conflicting_subjects_with_uppercase_days():
    """When replace=True and input days are uppercase names, old subjects are soft-deleted
    and a new subject is created successfully.
    """
    with PostgresContainer("postgres:15-alpine") as pg:
        engine = create_engine(pg.get_connection_url())
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create a user and student
        user = User(email="u2@example.com", name="U2", password_hash="hash")
        session.add(user)
        session.flush()

        student = StudentProfile(user_id=user.id, name="S2", school="X", grade="1")
        session.add(student)
        session.commit()

        repo = SubjectRepository(session)

        subj = repo.create(
            student_id=student.id,
            name="Fútbol",
            days=["Martes"],
            time=time(10, 0),
            teacher="Coach",
            color="#445566",
            type=SubjectType.EXTRAESCOLAR,
        )
        assert subj is not None

        # Replace using uppercase day input
        new_subj = repo.create(
            student_id=student.id,
            name="Fútbol NX",
            days=["MARTES"],
            time=time(10, 0),
            teacher="Coach",
            color="#445566",
            type=SubjectType.EXTRAESCOLAR,
            replace=True,
        )

        # The original should be marked deleted
        old = session.query(type(subj)).get(subj.id)
        assert old.deleted_at is not None
        assert new_subj is not None

        session.close()
        engine.dispose()
        Base.metadata.drop_all(bind=engine)
