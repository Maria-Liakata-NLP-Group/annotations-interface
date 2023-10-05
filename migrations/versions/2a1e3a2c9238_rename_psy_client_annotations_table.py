"""rename psy client annotations table

Revision ID: 2a1e3a2c9238
Revises: 2df180d7b7c5
Create Date: 2023-09-26 14:30:42.983877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a1e3a2c9238'
down_revision = '2df180d7b7c5'
branch_labels = None
depends_on = None


def upgrade():
    # rename the "ps_dialog_turn_annotation_client" table to "ps_annotation_client"
    op.rename_table('ps_dialog_turn_annotation_client', 'ps_annotation_client')


def downgrade():
    # rename the "ps_annotation_client" table to "ps_dialog_turn_annotation_client"
    op.rename_table('ps_annotation_client', 'ps_dialog_turn_annotation_client')

