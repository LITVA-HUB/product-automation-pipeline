from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260608_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("supplier", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("human_review_required", sa.Boolean(), nullable=False),
        sa.Column("review_reasons", sa.JSON(), nullable=False),
        sa.Column("candidate", sa.JSON(), nullable=False),
        sa.Column("article", sa.String(length=255), nullable=True),
        sa.Column("supplier_code", sa.String(length=255), nullable=True),
        sa.Column("ms_product_id", sa.String(length=255), nullable=True),
        sa.Column("ms_product_code", sa.String(length=255), nullable=True),
        sa.Column("site_product_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_supplier", "products", ["supplier"])
    op.create_index("ix_products_article", "products", ["article"])
    op.create_index("ix_products_supplier_code", "products", ["supplier_code"])
    op.create_index("ix_products_ms_product_code", "products", ["ms_product_code"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("actor", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("from_status", sa.String(length=64), nullable=True),
        sa.Column("to_status", sa.String(length=64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "validation_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("scope", sa.String(length=64), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("errors", sa.JSON(), nullable=False),
        sa.Column("validator_version", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "api_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.String(length=36), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("target", sa.String(length=64), nullable=False),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("endpoint", sa.Text(), nullable=False),
        sa.Column("request", sa.JSON(), nullable=False),
        sa.Column("response", sa.JSON(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("cost_estimate", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_api_requests_target", "api_requests", ["target"])


def downgrade() -> None:
    op.drop_index("ix_api_requests_target", table_name="api_requests")
    op.drop_table("api_requests")
    op.drop_table("validation_results")
    op.drop_table("audit_logs")
    op.drop_index("ix_products_ms_product_code", table_name="products")
    op.drop_index("ix_products_supplier_code", table_name="products")
    op.drop_index("ix_products_article", table_name="products")
    op.drop_index("ix_products_supplier", table_name="products")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_table("products")
