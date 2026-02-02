"""change days column from enum to text array

Revision ID: 20260202_0001
Revises: 20260201_0002
Create Date: 2026-02-02 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change days column from weekday[] enum to text[] to avoid serialization issues."""

    # Step 1: Add a temporary text[] column
    op.execute('ALTER TABLE subjects ADD COLUMN days_temp text[]')

    # Step 2: Copy data from days to days_temp, casting each enum value to text
    op.execute('''
        UPDATE subjects
        SET days_temp = ARRAY(
            SELECT unnest(days)::text
        )
    ''')

    # Step 3: Drop the old days column
    op.execute('ALTER TABLE subjects DROP COLUMN days')

    # Step 4: Rename days_temp to days
    op.execute('ALTER TABLE subjects RENAME COLUMN days_temp TO days')

    # Step 5: Add NOT NULL constraint back
    op.execute('ALTER TABLE subjects ALTER COLUMN days SET NOT NULL')

    # Note: We keep the weekday enum type in the database in case it's needed for other purposes
    # but subjects.days is now a simple text[] array


def downgrade() -> None:
    """Revert days column back to weekday[] enum."""

    # Step 1: Add a temporary weekday[] column
    op.execute('ALTER TABLE subjects ADD COLUMN days_temp weekday[]')

    # Step 2: Copy data from days to days_temp, casting text to enum
    op.execute('''
        UPDATE subjects
        SET days_temp = ARRAY(
            SELECT unnest(days)::weekday
        )
    ''')

    # Step 3: Drop the text days column
    op.execute('ALTER TABLE subjects DROP COLUMN days')

    # Step 4: Rename days_temp to days
    op.execute('ALTER TABLE subjects RENAME COLUMN days_temp TO days')

    # Step 5: Add NOT NULL constraint back
    op.execute('ALTER TABLE subjects ALTER COLUMN days SET NOT NULL')
