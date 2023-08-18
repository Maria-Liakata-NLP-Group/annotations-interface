"""Update enum values for sublabels

Revision ID: ab4c0ec94b46
Revises: af0f84a7f301
Create Date: 2023-08-18 17:44:58.307491

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = "ab4c0ec94b46"
down_revision = "af0f84a7f301"
branch_labels = None
depends_on = None


def upgrade():
    # for columns label_a, label_b, label_c, label_d, label_e update the value
    # "sublabel5" to "other" in the `ps_dialog_turn_annotation` table
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'other' WHERE label_a = 'sublabel5'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_b = 'other' WHERE label_b = 'sublabel5'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_c = 'other' WHERE label_c = 'sublabel5'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_d = 'other' WHERE label_d = 'sublabel5'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_e = 'other' WHERE label_e = 'sublabel5'"
        )
    )
    # modify the Enum definition to remove the sublabel5 value
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "label_a",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsa",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsa",
            ),
        )
        batch_op.alter_column(
            "label_b",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsb",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsb",
            ),
        )
        batch_op.alter_column(
            "label_c",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsc",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsc",
            ),
        )
        batch_op.alter_column(
            "label_d",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsd",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsd",
            ),
        )
        batch_op.alter_column(
            "label_e",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelse",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelse",
            ),
        )


def downgrade():
    # for columns label_a, label_b, label_c, label_d, label_e update the value
    # "other" to "sublabel5" in the `ps_dialog_turn_annotation` table
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_a = 'sublabel5' WHERE label_a = 'other'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_b = 'sublabel5' WHERE label_b = 'other'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_c = 'sublabel5' WHERE label_c = 'other'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_d = 'sublabel5' WHERE label_d = 'other'"
        )
    )
    op.execute(
        text(
            "UPDATE ps_dialog_turn_annotation SET label_e = 'sublabel5' WHERE label_e = 'other'"
        )
    )
    # modify the Enum definition to add the sublabel5 value
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
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsa",
            ),
        )
        batch_op.alter_column(
            "label_b",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsb",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsb",
            ),
        )
        batch_op.alter_column(
            "label_c",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsc",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsc",
            ),
        )
        batch_op.alter_column(
            "label_d",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelsd",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelsd",
            ),
        )
        batch_op.alter_column(
            "label_e",
            existing_type=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "other",
                name="sublabelse",
            ),
            nullable=True,
            type_=sa.Enum(
                "sublabel1",
                "sublabel2",
                "sublabel3",
                "sublabel4",
                "sublabel5",
                name="sublabelse",
            ),
        )
