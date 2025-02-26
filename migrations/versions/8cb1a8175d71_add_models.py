"""Add models

Revision ID: 8cb1a8175d71
Revises: 
Create Date: 2025-01-09 13:16:47.295395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8cb1a8175d71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('travel_plan', sa.Column('hotel_url', sa.String(length=200), nullable=True))
    op.add_column('travel_plan', sa.Column('confirmation_pdf', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('travel_plan', 'confirmation_pdf')
    op.drop_column('travel_plan', 'hotel_url')
    # ### end Alembic commands ###
