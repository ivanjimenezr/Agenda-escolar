"""update menu_items to use student_id

Revision ID: 003
Revises: 002
Create Date: 2026-01-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Drop existing constraint
    op.drop_constraint('unique_menu_per_date', 'menu_items', type_='unique')

    # Rename columns
    op.alter_column('menu_items', 'main_course', new_column_name='first_course')
    op.alter_column('menu_items', 'side_dish', existing_type=sa.String(255), nullable=True)
    op.alter_column('menu_items', 'dessert', existing_type=sa.String(255), nullable=True)

    # Add allergens column
    op.add_column('menu_items', sa.Column('allergens', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'))

    # Drop user_id and add student_id
    op.drop_constraint('menu_items_user_id_fkey', 'menu_items', type_='foreignkey')
    op.drop_column('menu_items', 'user_id')

    op.add_column('menu_items', sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key('menu_items_student_id_fkey', 'menu_items', 'student_profiles', ['student_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_menu_items_student_id'), 'menu_items', ['student_id'], unique=False)

    # Add new unique constraint
    op.create_unique_constraint('unique_menu_per_student_per_date', 'menu_items', ['student_id', 'date'])


def downgrade():
    # Reverse the changes
    op.drop_constraint('unique_menu_per_student_per_date', 'menu_items', type_='unique')
    op.drop_index(op.f('ix_menu_items_student_id'), table_name='menu_items')
    op.drop_constraint('menu_items_student_id_fkey', 'menu_items', type_='foreignkey')
    op.drop_column('menu_items', 'student_id')

    op.add_column('menu_items', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key('menu_items_user_id_fkey', 'menu_items', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_index('ix_menu_items_user_id', 'menu_items', ['user_id'], unique=False)

    op.drop_column('menu_items', 'allergens')
    op.alter_column('menu_items', 'dessert', existing_type=sa.String(255), nullable=False)
    op.alter_column('menu_items', 'side_dish', existing_type=sa.String(255), nullable=False)
    op.alter_column('menu_items', 'first_course', new_column_name='main_course')

    op.create_unique_constraint('unique_menu_per_date', 'menu_items', ['user_id', 'date'])
