"""add second_course to menu_items

Revision ID: 004
Revises: 003
Create Date: 2026-02-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Add column as nullable first to avoid issues with existing rows
    op.add_column('menu_items', sa.Column('second_course', sa.String(255), nullable=True))

    # Backfill existing rows with empty string to satisfy non-null constraint intent
    op.execute("UPDATE menu_items SET second_course = '' WHERE second_course IS NULL")

    # Alter column to be non-nullable and set a server default of empty string for safety
    op.alter_column('menu_items', 'second_course', existing_type=sa.String(255), nullable=False, server_default=sa.text("''"))


def downgrade():
    # Reverse: drop the column
    op.alter_column('menu_items', 'second_course', existing_type=sa.String(255), nullable=True, server_default=None)
    op.drop_column('menu_items', 'second_course')
