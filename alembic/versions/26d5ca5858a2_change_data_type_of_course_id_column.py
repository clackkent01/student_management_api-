"""Change data type of course id column

Revision ID: 26d5ca5858a2
Revises: 
Create Date: 2023-03-17 11:02:15.828377

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '26d5ca5858a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('course', 'id', type_=sa.String())


def downgrade():
    pass
