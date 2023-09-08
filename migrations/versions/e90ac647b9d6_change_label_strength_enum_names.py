"""change label strength enum names

Revision ID: e90ac647b9d6
Revises: 6a48bc97cce5
Create Date: 2023-09-08 09:02:27.616604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e90ac647b9d6"
down_revision = "6a48bc97cce5"
branch_labels = None
depends_on = None


def upgrade():
    # modify the Enum definition of the label strength to change the names
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "strength_a_client",
            existing_type=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthaclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthaclient",
            ),
        )
        batch_op.alter_column(
            "strength_b_client",
            existing_type=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthbclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthbclient",
            ),
        )
        batch_op.alter_column(
            "strength_c_client",
            existing_type=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthcclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthcclient",
            ),
        )
        batch_op.alter_column(
            "strength_d_client",
            existing_type=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthdclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthdclient",
            ),
        )
        batch_op.alter_column(
            "strength_e_client",
            existing_type=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengtheclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "no_recognition",
                "low_recognition",
                "moderate_recognition",
                "good_recognition",
                "excellent_recognition",
                name="labelstrengtheclient",
            ),
        )


def downgrade():
    # modify the Enum definition of the label strength to change the names
    with op.batch_alter_table("ps_dialog_turn_annotation", schema=None) as batch_op:
        batch_op.alter_column(
            "strength_a_client",
            existing_type=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthaclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthaclient",
            ),
        )
        batch_op.alter_column(
            "strength_b_client",
            existing_type=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthbclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthbclient",
            ),
        )
        batch_op.alter_column(
            "strength_c_client",
            existing_type=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthcclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthcclient",
            ),
        )
        batch_op.alter_column(
            "strength_d_client",
            existing_type=sa.Enum(
                "highly_maladaptive",
                "very_maladaptive",
                "moderately_adaptive",
                "very_adaptive",
                "highly_adaptive",
                name="labelstrengthdclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengthdclient",
            ),
        )
        batch_op.alter_column(
            "strength_e_client",
            existing_type=sa.Enum(
                "no_recognition",
                "low_recognition",
                "moderate_recognition",
                "good_recognition",
                "excellent_recognition",
                name="labelstrengtheclient",
            ),
            nullable=True,
            type_=sa.Enum(
                "strength1",
                "strength2",
                "strength3",
                "strength4",
                "strength5",
                name="labelstrengtheclient",
            ),
        )
