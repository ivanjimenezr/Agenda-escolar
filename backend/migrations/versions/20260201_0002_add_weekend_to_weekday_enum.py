"""add weekend days to weekday enum

Revision ID: 005
Revises: 004
Create Date: 2026-02-01 00:01:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Add 'Sábado' and 'Domingo' values to the existing `weekday` enum."""
    # Add values in an order that makes sense; Postgres allows adding new enum values.
    op.execute("ALTER TYPE weekday ADD VALUE IF NOT EXISTS 'Sábado'")
    op.execute("ALTER TYPE weekday ADD VALUE IF NOT EXISTS 'Domingo'")


def downgrade():
    """Downgrade is intentionally not implemented.

    Removing values from a PostgreSQL ENUM is non-trivial and may be destructive (existing
    rows using the values would make the operation fail or result in data loss). If you
    need to roll this back, perform a manual migration that:
      1) Ensures no rows contain the values to remove (or migrate them to other values),
      2) Creates a temporary ENUM type without the values,
      3) Alters the column to use the temporary type,
      4) Drops the old type and renames the temporary type to the original name.

    For safety we leave downgrade as a manual operation to avoid accidental data loss.
    """
    raise NotImplementedError("Downgrade not implemented: removing enum values is destructive and must be done manually.")