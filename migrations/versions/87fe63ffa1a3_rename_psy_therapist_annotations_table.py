"""rename psy therapist annotations table

Revision ID: 87fe63ffa1a3
Revises: 2a1e3a2c9238
Create Date: 2023-09-26 14:55:21.451626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87fe63ffa1a3'
down_revision = '2a1e3a2c9238'
branch_labels = None
depends_on = None


def upgrade():
    # rename "ps_dialog_turn_annotation_therapist" to "ps_annotation_therapist"
    op.rename_table('ps_dialog_turn_annotation_therapist', 'ps_annotation_therapist')


def downgrade():
    # rename "ps_annotation_therapist" to "ps_dialog_turn_annotation_therapist"
    op.rename_table('ps_annotation_therapist', 'ps_dialog_turn_annotation_therapist')

