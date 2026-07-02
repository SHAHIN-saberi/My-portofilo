"""fix education_translations: add degree and field_of_study columns

Revision ID: 0003_fix_education_translations
Revises: 0002_add_bm25_search_vector
Create Date: 2026-07-01 05:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_fix_education_translations"
down_revision = "0002_add_bm25_search_vector"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'degree' column to education_translations (NOT NULL - Python side always sets it)
    op.add_column(
        "education_translations",
        sa.Column("degree", sa.Text(), nullable=False, server_default=""),
    )
    # Add 'field_of_study' column to education_translations (nullable)
    op.add_column(
        "education_translations",
        sa.Column("field_of_study", sa.String(length=128), nullable=True),
    )
    # Ensure existing rows have a non-null degree (migrate empty strings to placeholder)
    op.execute(
        "UPDATE education_translations SET degree = 'Unknown' WHERE degree IS NULL OR degree = ''"
    )
    # Now make column truly NOT NULL after migration
    op.alter_column("education_translations", "degree", nullable=False)


def downgrade() -> None:
    op.drop_column("education_translations", "field_of_study")
    op.drop_column("education_translations", "degree")