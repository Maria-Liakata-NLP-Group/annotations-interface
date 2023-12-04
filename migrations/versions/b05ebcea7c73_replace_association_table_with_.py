"""replace association table with association object for client annotations-schema relationships

Revision ID: b05ebcea7c73
Revises: 3a72b32963cf
Create Date: 2023-12-04 16:00:38.458847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b05ebcea7c73"
down_revision = "3a72b32963cf"
branch_labels = None
depends_on = None


def upgrade():
    # remove the foreign key constraint on the `id_ps_annotation_client` and `id_client_annotation_schema` columns
    # then drop the table
    with op.batch_alter_table(
        "annotationclient_annotationschema", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_annotationclient_annotationschema_id_client_annotation_schema_client_annotation_schema",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "fk_annotationclient_annotationschema_id_ps_annotation_client_ps_annotation_client",
            type_="foreignkey",
        )
    op.drop_table("annotationclient_annotationschema")

    # create the table again, but with the `is_additional` column and with primary keys
    op.create_table(
        "annotationclient_annotationschema",
        sa.Column(
            "id_ps_annotation_client",
            sa.Integer(),
            sa.ForeignKey("ps_annotation_client.id"),
            primary_key=True,
        ),
        sa.Column(
            "id_client_annotation_schema",
            sa.Integer(),
            sa.ForeignKey("client_annotation_schema.id"),
            primary_key=True,
        ),
        sa.Column("is_additional", sa.Boolean(), default=False),
    )


def downgrade():
    op.drop_table("annotationclient_annotationschema")

    # create the table again, but without the `is_additional` column and without primary keys
    op.create_table(
        "annotationclient_annotationschema",
        sa.Column(
            "id_ps_annotation_client",
            sa.Integer(),
            sa.ForeignKey("ps_annotation_client.id"),
        ),
        sa.Column(
            "id_client_annotation_schema",
            sa.Integer(),
            sa.ForeignKey("client_annotation_schema.id"),
        ),
    )
