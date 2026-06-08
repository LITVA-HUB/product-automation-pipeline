from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260608_0003"
down_revision = "20260608_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "intake_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("operator_id", sa.String(length=255), nullable=True),
        sa.Column("chat_id", sa.String(length=255), nullable=True),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("raw_update", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_intake_events_source", "intake_events", ["source"])
    op.create_index("ix_intake_events_operator_id", "intake_events", ["operator_id"])
    op.create_index("ix_intake_events_kind", "intake_events", ["kind"])
    op.create_index("ix_intake_events_status", "intake_events", ["status"])


def downgrade() -> None:
    op.drop_index("ix_intake_events_status", table_name="intake_events")
    op.drop_index("ix_intake_events_kind", table_name="intake_events")
    op.drop_index("ix_intake_events_operator_id", table_name="intake_events")
    op.drop_index("ix_intake_events_source", table_name="intake_events")
    op.drop_table("intake_events")
