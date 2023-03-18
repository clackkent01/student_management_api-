"""empty message

Revision ID: 133980f8d61d
Revises: 
Create Date: 2023-03-18 01:17:02.927023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '133980f8d61d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)

    with op.batch_alter_table('student_course', schema=None) as batch_op:
        batch_op.alter_column('course_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.create_unique_constraint('_student_course_uc', ['student_id', 'course_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student_course', schema=None) as batch_op:
        batch_op.drop_constraint('_student_course_uc', type_='unique')
        batch_op.alter_column('course_id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('course', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
