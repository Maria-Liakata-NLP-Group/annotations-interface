"""update label A attachment enum

Revision ID: 9a1b81643c98
Revises: c92a9208d21b
Create Date: 2023-08-24 12:49:36.720063

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = '9a1b81643c98'
down_revision = 'c92a9208d21b'
branch_labels = None
depends_on = None


def upgrade():
    # update the value of label_a from sublabel1 to attachment
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'attachment' WHERE label_a = 'sublabel1'"
        )
    )
    # modify the Enum definition to remove the sublabel1 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
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


def downgrade():
    # update the value of label_a from attachment to sublabel1
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'sublabel1' WHERE label_a = 'attachment'"
        )
    )
    # modify the Enum definition to add the sublabel1 value
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
                "sublabel1",
                "attachment",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
        )
