"""Multi-tenancy and project ownership

Revision ID: 003
Revises: 002
Create Date: 2025-10-28

Adds multi-tenancy features:
- User system_user field for SSH deployment
- Project ownership (owner_id FK)
- Slug-based project paths

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    """Check if column exists in table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c['name'] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # Add system_user to users table if doesn't exist
    if not column_exists('users', 'system_user'):
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('system_user', sa.String(length=255), nullable=False, server_default='docklite'))
    
    # Add slug, owner_id to projects table if don't exist
    if not column_exists('projects', 'slug'):
        with op.batch_alter_table('projects') as batch_op:
            batch_op.add_column(sa.Column('slug', sa.String(length=255), nullable=True))  # Nullable initially
            batch_op.create_index('ix_projects_slug', ['slug'], unique=True)
    
    if not column_exists('projects', 'owner_id'):
        with op.batch_alter_table('projects') as batch_op:
            batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=True))  # Nullable initially
            batch_op.create_index('ix_projects_owner_id', ['owner_id'], unique=False)
            batch_op.create_foreign_key('fk_projects_owner_id', 'users', ['owner_id'], ['id'])


def downgrade() -> None:
    # Drop project columns with batch mode
    with op.batch_alter_table('projects') as batch_op:
        batch_op.drop_constraint('fk_projects_owner_id', type_='foreignkey')
        batch_op.drop_index('ix_projects_owner_id')
        batch_op.drop_index('ix_projects_slug')
        batch_op.drop_column('owner_id')
        batch_op.drop_column('slug')
    
    # Drop user column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('system_user')

