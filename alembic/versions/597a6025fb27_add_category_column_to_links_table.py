"""add category column to links table

Revision ID: 597a6025fb27
Revises: 
Create Date: 2020-10-31 15:14:29.824422

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision = '597a6025fb27'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Adds the category column in.
    """
    op.add_column('link', Column('category', String(length=255)))


def downgrade():
    """Removes the category column.
    """
    op.drop_column('link', 'category')
