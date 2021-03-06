"""empty message

Revision ID: 6f2a89e50fa5
Revises: 718f0e4a64a6
Create Date: 2020-12-10 13:41:28.006350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f2a89e50fa5'
down_revision = '718f0e4a64a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('demo', 'name',
               existing_type=sa.VARCHAR(length=500),
               comment='名字',
               existing_nullable=True)
    op.alter_column('demo', 'num',
               existing_type=sa.NUMERIC(precision=20, scale=5),
               comment='数字',
               existing_nullable=True)
    op.create_unique_constraint(None, 'demo', ['id'])
    op.create_unique_constraint(None, 'demo_item', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'demo_item', type_='unique')
    op.drop_constraint(None, 'demo', type_='unique')
    op.alter_column('demo', 'num',
               existing_type=sa.NUMERIC(precision=20, scale=5),
               comment=None,
               existing_comment='数字',
               existing_nullable=True)
    op.alter_column('demo', 'name',
               existing_type=sa.VARCHAR(length=500),
               comment=None,
               existing_comment='名字',
               existing_nullable=True)
    # ### end Alembic commands ###
