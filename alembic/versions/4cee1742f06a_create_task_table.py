"""create task table

Revision ID: 4cee1742f06a
Revises: 8ca086938ec8
Create Date: 2022-04-13 17:38:25.603337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4cee1742f06a'
down_revision = '8ca086938ec8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tasks',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('deadline', sa.Date(), nullable=True),
                    sa.Column('completed', sa.Boolean(create_constraint=False),
                              server_default=sa.sql.expression.false(), nullable=False),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
                    sa.Column('last_update', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='tasks_owner_id_fkey', ondelete='CASCADE'),
                    )


def downgrade():
    op.drop_table('tasks')
