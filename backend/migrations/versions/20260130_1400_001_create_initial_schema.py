"""create initial schema

Revision ID: 001
Revises:
Create Date: 2026-01-30 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("CREATE TYPE subject_type AS ENUM ('colegio', 'extraescolar')")
    op.execute("CREATE TYPE weekday AS ENUM ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')")
    op.execute("CREATE TYPE event_type AS ENUM ('Festivo', 'Lectivo', 'Vacaciones')")
    op.execute("CREATE TYPE theme_type AS ENUM ('light', 'dark')")

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create student_profiles table
    op.create_table(
        'student_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('school', sa.String(255), nullable=False),
        sa.Column('grade', sa.String(100), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('allergies', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('excluded_foods', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_student_profiles_user_id', 'student_profiles', ['user_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create active_modules table
    op.create_table(
        'active_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('subjects', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('exams', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('menu', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('events', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('dinner', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('contacts', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_active_modules_student', 'active_modules', ['student_id'], unique=True)

    # Create subjects table
    op.create_table(
        'subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('days', postgresql.ARRAY(postgresql.ENUM('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', name='weekday', create_type=False)), nullable=False),
        sa.Column('time', sa.Time(), nullable=False),
        sa.Column('teacher', sa.String(255), nullable=False),
        sa.Column('color', sa.String(7), nullable=False),
        sa.Column('type', postgresql.ENUM('colegio', 'extraescolar', name='subject_type', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("color ~ '^#[0-9A-Fa-f]{6}$'", name='valid_color'),
        sa.CheckConstraint('array_length(days, 1) >= 1', name='at_least_one_day'),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_subjects_student_id', 'subjects', ['student_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.execute('CREATE INDEX idx_subjects_days ON subjects USING GIN(days)')

    # Create exams table
    op.create_table(
        'exams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_exams_student_date', 'exams', ['student_id', 'date'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_exams_upcoming', 'exams', ['date'], unique=False, postgresql_where=sa.text("date >= CURRENT_DATE AND deleted_at IS NULL"))

    # Create menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('main_course', sa.String(255), nullable=False),
        sa.Column('side_dish', sa.String(255), nullable=False),
        sa.Column('dessert', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'date', name='unique_menu_per_date'),
    )
    op.create_index('idx_menu_items_date', 'menu_items', ['date'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_menu_items_user_date', 'menu_items', ['user_id', 'date'], unique=False)

    # Create dinners table
    op.create_table(
        'dinners',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('meal', sa.Text(), nullable=False),
        sa.Column('ingredients', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['student_profiles.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('student_id', 'date', name='unique_dinner_per_student_date'),
    )
    op.create_index('idx_dinners_student_date', 'dinners', ['student_id', 'date'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create school_events table
    op.create_table(
        'school_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', postgresql.ENUM('Festivo', 'Lectivo', 'Vacaciones', name='event_type', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_events_user_date', 'school_events', ['user_id', 'date'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_events_upcoming', 'school_events', ['date'], unique=False, postgresql_where=sa.text("date >= CURRENT_DATE AND deleted_at IS NULL"))

    # Create centers table
    op.create_table(
        'centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_centers_user_id', 'centers', ['user_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('center_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('role', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['center_id'], ['centers.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_contacts_center_id', 'contacts', ['center_id'], unique=False, postgresql_where=sa.text('deleted_at IS NULL'))

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('theme', postgresql.ENUM('light', 'dark', name='theme_type', create_type=False), nullable=False, server_default=sa.text("'light'")),
        sa.Column('card_order', postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{subjects,menu,dinner,exams,contacts}'")),
        sa.Column('active_profile_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['active_profile_id'], ['student_profiles.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_user_preferences_user', 'user_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_index('idx_user_preferences_user', table_name='user_preferences')
    op.drop_table('user_preferences')

    op.drop_index('idx_contacts_center_id', table_name='contacts')
    op.drop_table('contacts')

    op.drop_index('idx_centers_user_id', table_name='centers')
    op.drop_table('centers')

    op.drop_index('idx_events_upcoming', table_name='school_events')
    op.drop_index('idx_events_user_date', table_name='school_events')
    op.drop_table('school_events')

    op.drop_index('idx_dinners_student_date', table_name='dinners')
    op.drop_table('dinners')

    op.drop_index('idx_menu_items_user_date', table_name='menu_items')
    op.drop_index('idx_menu_items_date', table_name='menu_items')
    op.drop_table('menu_items')

    op.drop_index('idx_exams_upcoming', table_name='exams')
    op.drop_index('idx_exams_student_date', table_name='exams')
    op.drop_table('exams')

    op.execute('DROP INDEX IF EXISTS idx_subjects_days')
    op.drop_index('idx_subjects_student_id', table_name='subjects')
    op.drop_table('subjects')

    op.drop_index('idx_active_modules_student', table_name='active_modules')
    op.drop_table('active_modules')

    op.drop_index('idx_student_profiles_user_id', table_name='student_profiles')
    op.drop_table('student_profiles')

    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS theme_type')
    op.execute('DROP TYPE IF EXISTS event_type')
    op.execute('DROP TYPE IF EXISTS weekday')
    op.execute('DROP TYPE IF EXISTS subject_type')
