"""Add phone_number column manually

Revision ID: 66f08ca0141b
Revises: 
Create Date: 2025-05-18 04:20:44.256799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66f08ca0141b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))


def downgrade():
    op.drop_column('users', 'phone_number')
