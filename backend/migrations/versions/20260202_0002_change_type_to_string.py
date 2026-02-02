"""change type column from enum to string

Revision ID: 007
Revises: 006
Create Date: 2026-02-02 23:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change type column from subject_type enum to varchar to avoid serialization issues."""

    # Step 1: Add a temporary varchar column
    op.execute('ALTER TABLE subjects ADD COLUMN type_temp varchar(50)')

    # Step 2: Copy data from type to type_temp, casting enum to text
    op.execute('''
        UPDATE subjects
        SET type_temp = type::text
    ''')

    # Step 3: Drop the old type column
    op.execute('ALTER TABLE subjects DROP COLUMN type')

    # Step 4: Rename type_temp to type
    op.execute('ALTER TABLE subjects RENAME COLUMN type_temp TO type')

    # Step 5: Add NOT NULL constraint back
    op.execute('ALTER TABLE subjects ALTER COLUMN type SET NOT NULL')

    # Note: We keep the subject_type enum in the database in case it's needed for other purposes


def downgrade() -> None:
    """Revert type column back to subject_type enum."""

    # Step 1: Add a temporary subject_type enum column
    op.execute('ALTER TABLE subjects ADD COLUMN type_temp subject_type')

    # Step 2: Copy data from type to type_temp, casting text to enum
    op.execute('''
        UPDATE subjects
        SET type_temp = type::subject_type
    ''')

    # Step 3: Drop the varchar type column
    op.execute('ALTER TABLE subjects DROP COLUMN type')

    # Step 4: Rename type_temp to type
    op.execute('ALTER TABLE subjects RENAME COLUMN type_temp TO type')

    # Step 5: Add NOT NULL constraint back
    op.execute('ALTER TABLE subjects ALTER COLUMN type SET NOT NULL')
