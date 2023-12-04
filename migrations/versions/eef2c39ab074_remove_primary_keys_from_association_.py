"""remove primary keys from association object

Revision ID: eef2c39ab074
Revises: b05ebcea7c73
Create Date: 2023-12-04 17:26:49.161804

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eef2c39ab074"
down_revision = "b05ebcea7c73"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "annotationclient_annotationschema", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "pk_annotationclient_annotationschema", type_="primary"
        )
        batch_op.add_column(sa.Column("id", sa.Integer(), nullable=False))
        batch_op.create_primary_key(
            "pk_annotationclient_annotationschema", ["id"]
        )


def downgrade():
    with op.batch_alter_table(
        "annotationclient_annotationschema", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "pk_annotationclient_annotationschema", type_="primary"
        )
        batch_op.drop_column("id")
        batch_op.create_primary_key(
            "pk_annotationclient_annotationschema",
            ["annotationclient_id", "annotationschema_id"],
        )
