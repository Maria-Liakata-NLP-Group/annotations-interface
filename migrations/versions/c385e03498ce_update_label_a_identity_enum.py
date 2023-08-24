"""update label A identity enum

Revision ID: c385e03498ce
Revises: 9a1b81643c98
Create Date: 2023-08-24 15:39:12.915038

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'c385e03498ce'
down_revision = '9a1b81643c98'
branch_labels = None
depends_on = None


def upgrade():
    # update the value of label_a from sublabel2 to identity
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'identity' WHERE label_a = 'sublabel2'"
        )
    )
    # modify the Enum definition to remove the sublabel2 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "attachment",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
            nullable=True,
            type_=sa.Enum(
                "attachment",
                "identity",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
        )


def downgrade():
    # update the value of label_a from identity to sublabel2
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'sublabel2' WHERE label_a = 'identity'"
        )
    )
    # modify the Enum definition to add the sublabel2 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "attachment",
                "identity",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
            nullable=True,
            type_=sa.Enum(
                "attachment",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
        )
