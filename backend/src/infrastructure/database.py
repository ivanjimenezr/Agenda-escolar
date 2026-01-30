"""
Database connection configuration for PostgreSQL.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
from typing import Generator

from .config import settings

# Create SQLAlchemy engine
# Using connection pooling with optimized settings
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using them
    echo=settings.debug,  # SQL query logging in debug mode
)


# Configure connection pool to handle network issues gracefully
@event.listens_for(Pool, "connect")
def set_connection_parameters(dbapi_conn, connection_record):
    """Set connection parameters for better timeout handling."""
    cursor = dbapi_conn.cursor()
    cursor.execute("SET statement_timeout = '30s'")  # 30 second query timeout
    cursor.execute("SET idle_in_transaction_session_timeout = '60s'")  # 60 second idle timeout
    cursor.close()


# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI endpoints:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            ...

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    This creates all tables defined in SQLAlchemy models.

    Note: In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)


def close_db():
    """
    Close all database connections.
    Call this during application shutdown.
    """
    engine.dispose()
