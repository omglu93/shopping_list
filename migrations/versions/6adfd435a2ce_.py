"""empty message

Revision ID: 6adfd435a2ce
Revises: 70ec9924c92f
Create Date: 2022-03-04 22:22:17.605495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6adfd435a2ce'
down_revision = '70ec9924c92f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shopinglist_table', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'shopinglist_table', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shopinglist_table', type_='foreignkey')
    op.drop_column('shopinglist_table', 'user_id')
    # ### end Alembic commands ###
