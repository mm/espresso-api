"""Adds collection_id to Link

Revision ID: a5ce356ac45f
Revises: 63616e5cabb3
Create Date: 2021-05-24 11:01:22.115123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5ce356ac45f"
down_revision = "63616e5cabb3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("link", sa.Column("collection_id", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("link", "collection_id")
    # ### end Alembic commands ###
