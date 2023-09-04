"""update label A excitement enum

Revision ID: d06f3814442c
Revises: d4e163031ff6
Create Date: 2023-08-24 21:00:05.078682

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'd06f3814442c'
down_revision = 'd4e163031ff6'
branch_labels = None
depends_on = None


def upgrade():
    # update the value of label_a from sublabel4 to excitement
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'excitement' WHERE label_a = 'sublabel4'"
        )
    )

    # modify the Enum definition to remove the sublabel4 value
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
                "security",
                "excitement",
                "other",
                name="sublabelsa",
            ),
        )


def downgrade():
    # update the value of label_a from excitement to sublabel4
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'sublabel4' WHERE label_a = 'excitement'"
        )
    )

    # modify the Enum definition to add the sublabel4 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "attachment",
                "identity",
                "security",
                "excitement",
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
