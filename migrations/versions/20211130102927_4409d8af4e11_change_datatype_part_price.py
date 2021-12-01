"""change datatype part price

Revision ID: 4409d8af4e11
Revises: e7ff52db4b2f
Create Date: 2021-11-30 10:29:27.563440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4409d8af4e11'
down_revision = 'e7ff52db4b2f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('part', 'price',
               existing_type=sa.BOOLEAN(),
               type_=sa.Numeric(),
               existing_nullable=False,
               postgresql_using="\"price\"::bool::int::numeric")
    # ### end Alembic commands ###
    op.execute("COMMIT")

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('part', 'price',
               existing_type=sa.Numeric(),
               type_=sa.BOOLEAN(),
               existing_nullable=False,
               postgresql_using="\"price\"::bool")
    # ### end Alembic commands ###
    op.execute("COMMIT")
