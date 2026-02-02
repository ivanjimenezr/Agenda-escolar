"""
SQLAlchemy ORM Models for Agenda Escolar Pro.
All models follow the database schema design.
"""
from datetime import datetime, time, date
from typing import List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Text,
    CheckConstraint,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import JSON
import uuid
import enum

from src.infrastructure.database import Base
from src.infrastructure.config import settings

# Detect whether configured DB URL points to SQLite. This is used only for
# some module-level decisions (like default values and table constraints).
_using_sqlite = settings.database_url.startswith("sqlite")

# ArrayType: a dialect-aware column type that uses native Postgres ARRAY
# when the dialect is postgresql, and JSON for other dialects (e.g., SQLite in tests).
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy import String

class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type when available, otherwise stores UUIDs as
    36-char strings on other dialects (SQLite for tests).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        # store as string for non-postgres
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return value
        return uuid.UUID(value)


class ArrayType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def __init__(self, item_type, pg_kwargs=None):
        self.item_type = item_type
        self.pg_kwargs = pg_kwargs or {}
        super().__init__()

    def load_dialect_impl(self, dialect):
        # Use native ARRAY on PostgreSQL, JSON otherwise
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(self.item_type, **self.pg_kwargs))
        return dialect.type_descriptor(JSON)


# ================ ENUMS ================

class SubjectType(str, enum.Enum):
    """Subject type enumeration."""
    COLEGIO = "colegio"
    EXTRAESCOLAR = "extraescolar"


class Weekday(str, enum.Enum):
    """Weekday enumeration in Spanish."""
    LUNES = "Lunes"
    MARTES = "Martes"
    MIERCOLES = "Miércoles"
    JUEVES = "Jueves"
    VIERNES = "Viernes"
    SABADO = "Sábado"
    DOMINGO = "Domingo"


class EventType(str, enum.Enum):
    """School event type enumeration."""
    FESTIVO = "Festivo"
    LECTIVO = "Lectivo"
    VACACIONES = "Vacaciones"


class ThemeType(str, enum.Enum):
    """UI theme type enumeration."""
    LIGHT = "light"
    DARK = "dark"


# ================ MODELS ================

class User(Base):
    """User model - represents a parent/guardian account."""
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student_profiles = relationship("StudentProfile", back_populates="user", cascade="all, delete-orphan")
    school_events = relationship("SchoolEvent", back_populates="user", cascade="all, delete-orphan")
    centers = relationship("Center", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class StudentProfile(Base):
    """Student profile model - represents a child/student."""
    __tablename__ = "student_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    school = Column(String(255), nullable=False)
    grade = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    allergies = Column(ArrayType(Text), nullable=False, default=list)
    excluded_foods = Column(ArrayType(Text), nullable=False, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profiles")
    active_modules = relationship("ActiveModule", back_populates="student", uselist=False, cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="student", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="student", cascade="all, delete-orphan")
    dinners = relationship("Dinner", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudentProfile(id={self.id}, name='{self.name}', grade='{self.grade}')>"


# Backwards compatibility alias: some deployed/older code used the name `Student`.
# Providing this alias ensures relationships referencing 'Student' still resolve
# during SQLAlchemy mapper initialization and prevents InvalidRequestError.
Student = StudentProfile

class ActiveModule(Base):
    """Active modules configuration per student."""
    __tablename__ = "active_modules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Module flags
    subjects = Column(Boolean, default=True, nullable=False)
    exams = Column(Boolean, default=True, nullable=False)
    menu = Column(Boolean, default=True, nullable=False)
    events = Column(Boolean, default=True, nullable=False)
    dinner = Column(Boolean, default=True, nullable=False)
    contacts = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    student = relationship("StudentProfile", back_populates="active_modules")

    def __repr__(self):
        return f"<ActiveModule(student_id={self.student_id})>"


class Subject(Base):
    """Subject model - represents classes and extracurricular activities."""
    __tablename__ = "subjects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    # Store weekdays as simple text array (no enum to avoid serialization issues)
    days = Column(ArrayType(Text), nullable=False)
    time = Column(Time, nullable=False)
    teacher = Column(String(255), nullable=True)
    color = Column(String(7), nullable=False)
    # Changed from enum to String to avoid serialization issues
    type = Column(String(50), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Constraints
    # Table constraints removed to keep model cross-dialect compatible during tests.
    __table_args__ = ()

    # Relationships
    student = relationship("StudentProfile", back_populates="subjects")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', type={self.type})>"


class Exam(Base):
    """Exam model - represents upcoming tests and exams."""
    __tablename__ = "exams"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    date = Column(Date, nullable=False)
    topic = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    student = relationship("StudentProfile", back_populates="exams")

    def __repr__(self):
        return f"<Exam(id={self.id}, subject='{self.subject}', date={self.date})>"


class MenuItem(Base):
    """Menu item model - represents school lunch menu."""
    __tablename__ = "menu_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    first_course = Column(String(255), nullable=False)
    second_course = Column(String(255), nullable=False)
    side_dish = Column(String(255), nullable=True)
    dessert = Column(String(255), nullable=True)
    allergens = Column(ArrayType(String), default=list, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="unique_menu_per_student_per_date"),
    )

    # Relationships
    student = relationship("StudentProfile", back_populates="menu_items")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, date={self.date}, first_course='{self.first_course}')>"


class Dinner(Base):
    """Dinner model - represents AI-suggested dinners."""
    __tablename__ = "dinners"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    student_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    meal = Column(Text, nullable=False)
    ingredients = Column(ArrayType(Text), nullable=False, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("student_id", "date", name="unique_dinner_per_student_date"),
    )

    # Relationships
    student = relationship("StudentProfile", back_populates="dinners")

    def __repr__(self):
        return f"<Dinner(id={self.id}, date={self.date}, meal='{self.meal}')>"


class SchoolEvent(Base):
    """School event model - represents calendar events."""
    __tablename__ = "school_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(EventType, name="event_type", create_type=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="school_events")

    def __repr__(self):
        return f"<SchoolEvent(id={self.id}, name='{self.name}', date={self.date}, type={self.type})>"


class Center(Base):
    """Center model - represents educational centers/institutions."""
    __tablename__ = "centers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="centers")
    contacts = relationship("Contact", back_populates="center", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Center(id={self.id}, name='{self.name}')>"


class Contact(Base):
    """Contact model - represents directory contacts."""
    __tablename__ = "contacts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    center_id = Column(GUID(), ForeignKey("centers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    role = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    center = relationship("Center", back_populates="contacts")

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}', phone='{self.phone}')>"


class UserPreference(Base):
    """User preferences model - UI preferences and settings."""
    __tablename__ = "user_preferences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    theme = Column(SQLEnum(ThemeType, name="theme_type", create_type=True), default=ThemeType.LIGHT, nullable=False)
    card_order = Column(ArrayType(Text), nullable=False, default=list)
    active_profile_id = Column(GUID(), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, theme={self.theme})>"
