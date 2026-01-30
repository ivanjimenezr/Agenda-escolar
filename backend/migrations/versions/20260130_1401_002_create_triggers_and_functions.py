"""create triggers and functions

Revision ID: 002
Revises: 001
Create Date: 2026-01-30 14:01:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create function to automatically update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create triggers for all tables with updated_at column
    tables_with_updated_at = [
        'users',
        'student_profiles',
        'active_modules',
        'subjects',
        'exams',
        'menu_items',
        'dinners',
        'school_events',
        'centers',
        'contacts',
        'user_preferences',
    ]

    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)

    # Create function to automatically create default active_modules for new students
    op.execute("""
        CREATE OR REPLACE FUNCTION create_default_active_modules()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO active_modules (student_id)
            VALUES (NEW.id);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to auto-create active_modules when student_profile is created
    op.execute("""
        CREATE TRIGGER trigger_create_default_active_modules
        AFTER INSERT ON student_profiles
        FOR EACH ROW
        EXECUTE FUNCTION create_default_active_modules();
    """)

    # Create function to automatically create default user_preferences for new users
    op.execute("""
        CREATE OR REPLACE FUNCTION create_default_user_preferences()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO user_preferences (user_id)
            VALUES (NEW.id);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to auto-create user_preferences when user is created
    op.execute("""
        CREATE TRIGGER trigger_create_default_user_preferences
        AFTER INSERT ON users
        FOR EACH ROW
        EXECUTE FUNCTION create_default_user_preferences();
    """)


def downgrade() -> None:
    # Drop triggers for user_preferences
    op.execute("DROP TRIGGER IF EXISTS trigger_create_default_user_preferences ON users")
    op.execute("DROP FUNCTION IF EXISTS create_default_user_preferences()")

    # Drop triggers for active_modules
    op.execute("DROP TRIGGER IF EXISTS trigger_create_default_active_modules ON student_profiles")
    op.execute("DROP FUNCTION IF EXISTS create_default_active_modules()")

    # Drop updated_at triggers
    tables_with_updated_at = [
        'users',
        'student_profiles',
        'active_modules',
        'subjects',
        'exams',
        'menu_items',
        'dinners',
        'school_events',
        'centers',
        'contacts',
        'user_preferences',
    ]

    for table in tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")

    # Drop the update_updated_at_column function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
