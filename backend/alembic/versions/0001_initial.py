"""Initial schema: roi_detections table

Revision ID: 0001
Revises:
Create Date: 2026-05-05
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "roi_detections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False),
        sa.Column("frame_number", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("bbox_x", sa.Float(), nullable=False),
        sa.Column("bbox_y", sa.Float(), nullable=False),
        sa.Column("bbox_width", sa.Float(), nullable=False),
        sa.Column("bbox_height", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("frame_width", sa.Integer(), nullable=False),
        sa.Column("frame_height", sa.Integer(), nullable=False),
        sa.CheckConstraint("frame_number >= 0", name="ck_roi_frame_number_nonneg"),
        sa.CheckConstraint("confidence >= 0 AND confidence <= 1", name="ck_roi_confidence_range"),
    )

    op.create_index("idx_roi_session_ts", "roi_detections", ["session_id", sa.text("timestamp DESC")])
    op.create_index("idx_roi_frame", "roi_detections", ["session_id", "frame_number"])


def downgrade() -> None:
    op.drop_index("idx_roi_frame", table_name="roi_detections")
    op.drop_index("idx_roi_session_ts", table_name="roi_detections")
    op.drop_table("roi_detections")
