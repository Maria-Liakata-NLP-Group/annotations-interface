"""rename psy dyad annotations table

Revision ID: f77d253b05cc
Revises: 87fe63ffa1a3
Create Date: 2023-09-26 15:16:56.799187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f77d253b05cc'
down_revision = '87fe63ffa1a3'
branch_labels = None
depends_on = None


def upgrade():
    # rename the "ps_dialog_turn_annotation_dyad" to "ps_annotation_dyad"
    op.rename_table('ps_dialog_turn_annotation_dyad', 'ps_annotation_dyad')


def downgrade():
    # rename the "ps_annotation_dyad" to "ps_dialog_turn_annotation_dyad"
    op.rename_table('ps_annotation_dyad', 'ps_dialog_turn_annotation_dyad')
