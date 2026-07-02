"""add bm25 full-text search index to knowledge_chunks

Revision ID: 0002_add_bm25_search_vector
Revises: 0001_initial
Create Date: 2026-07-01 04:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_bm25_search_vector"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tsvector columns for BM25 full-text search (multilingual).
    # Populated automatically via a BEFORE INSERT trigger.
    op.add_column(
        "knowledge_chunks",
        sa.Column("search_vector_en", sa.dialects.postgresql.TSVECTOR(), nullable=True),
    )
    op.add_column(
        "knowledge_chunks",
        sa.Column("search_vector_fa", sa.dialects.postgresql.TSVECTOR(), nullable=True),
    )
    # GIN indexes for fast BM25 ranking via ts_rank / plainto_tsquery
    op.create_index(
        "idx_knowledge_chunks_search_en",
        "knowledge_chunks",
        ["search_vector_en"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_knowledge_chunks_search_fa",
        "knowledge_chunks",
        ["search_vector_fa"],
        postgresql_using="gin",
    )

    # Trigger that auto-populates tsvector columns from chunk_text on INSERT.
    # English config for en chunks, 'simple' config for fa chunks (no dedicated
    # Persian stemmer in standard PostgreSQL). We weight sections so titles
    # rank higher than body text.
    op.execute("""
        CREATE OR REPLACE FUNCTION _populate_search_vectors()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Always index English tsvector from chunk_text
            NEW.search_vector_en := setweight(
                to_tsvector('english', coalesce(NEW.chunk_text, '')),
                'B'
            );
            -- Always index Persian tsvector from chunk_text using simple config
            NEW.search_vector_fa := setweight(
                to_tsvector('simple', coalesce(NEW.chunk_text, '')),
                'B'
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_knowledge_chunks_search_vectors
        BEFORE INSERT ON knowledge_chunks
        FOR EACH ROW
        EXECUTE FUNCTION _populate_search_vectors();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_knowledge_chunks_search_vectors ON knowledge_chunks;")
    op.execute("DROP FUNCTION IF EXISTS _populate_search_vectors();")
    op.drop_index("idx_knowledge_chunks_search_fa", table_name="knowledge_chunks")
    op.drop_index("idx_knowledge_chunks_search_en", table_name="knowledge_chunks")
    op.drop_column("knowledge_chunks", "search_vector_fa")
    op.drop_column("knowledge_chunks", "search_vector_en")