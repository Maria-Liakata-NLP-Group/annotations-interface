"""update label A security enum

Revision ID: d4e163031ff6
Revises: c385e03498ce
Create Date: 2023-08-24 16:50:53.821913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'd4e163031ff6'
down_revision = 'c385e03498ce'
branch_labels = None
depends_on = None


def upgrade():
    # update the value of label_a from sublabel3 to security
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'security' WHERE label_a = 'sublabel3'"
        )
    )
    # modify the Enum definition to remove the sublabel3 value
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
                "identity",
                "security",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
        )


def downgrade():
    # update the value of label_a from security to sublabel3
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'sublabel3' WHERE label_a = 'security'"
        )
    )
    # modify the Enum definition to add the sublabel3 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "attachment",
                "identity",
                "security",
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
