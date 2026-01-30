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
import uuid
import enum

from src.infrastructure.database import Base


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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    menu_items = relationship("MenuItem", back_populates="user", cascade="all, delete-orphan")
    school_events = relationship("SchoolEvent", back_populates="user", cascade="all, delete-orphan")
    centers = relationship("Center", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"


class StudentProfile(Base):
    """Student profile model - represents a child/student."""
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    school = Column(String(255), nullable=False)
    grade = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)
    allergies = Column(ARRAY(Text), nullable=False, server_default="{}")
    excluded_foods = Column(ARRAY(Text), nullable=False, server_default="{}")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="student_profiles")
    active_modules = relationship("ActiveModule", back_populates="student", uselist=False, cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="student", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="student", cascade="all, delete-orphan")
    dinners = relationship("Dinner", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudentProfile(id={self.id}, name='{self.name}', grade='{self.grade}')>"


class ActiveModule(Base):
    """Active modules configuration per student."""
    __tablename__ = "active_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    days = Column(ARRAY(SQLEnum(Weekday, name="weekday", create_type=True)), nullable=False)
    time = Column(Time, nullable=False)
    teacher = Column(String(255), nullable=False)
    color = Column(String(7), nullable=False)
    type = Column(SQLEnum(SubjectType, name="subject_type", create_type=True), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name="valid_color"),
        CheckConstraint("array_length(days, 1) >= 1", name="at_least_one_day"),
    )

    # Relationships
    student = relationship("StudentProfile", back_populates="subjects")

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', type={self.type})>"


class Exam(Base):
    """Exam model - represents upcoming tests and exams."""
    __tablename__ = "exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    main_course = Column(String(255), nullable=False)
    side_dish = Column(String(255), nullable=False)
    dessert = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="unique_menu_per_date"),
    )

    # Relationships
    user = relationship("User", back_populates="menu_items")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, date={self.date}, main_course='{self.main_course}')>"


class Dinner(Base):
    """Dinner model - represents AI-suggested dinners."""
    __tablename__ = "dinners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    meal = Column(Text, nullable=False)
    ingredients = Column(ARRAY(Text), nullable=False, server_default="{}")

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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    center_id = Column(UUID(as_uuid=True), ForeignKey("centers.id", ondelete="CASCADE"), nullable=False, index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    theme = Column(SQLEnum(ThemeType, name="theme_type", create_type=True), default=ThemeType.LIGHT, nullable=False)
    card_order = Column(ARRAY(Text), nullable=False, server_default='{"subjects","menu","dinner","exams","contacts"}')
    active_profile_id = Column(UUID(as_uuid=True), ForeignKey("student_profiles.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreference(user_id={self.user_id}, theme={self.theme})>"
