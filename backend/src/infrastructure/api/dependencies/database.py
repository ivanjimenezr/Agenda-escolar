"""
Database Dependencies

FastAPI dependency for database session injection
"""

from typing import Generator

from sqlalchemy.orm import Session

from src.infrastructure.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it's closed after the request.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
