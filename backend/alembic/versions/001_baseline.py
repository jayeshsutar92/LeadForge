"""001 – Baseline schema for all LeadForge tables.

Creates: users, businesses, business_contacts, search_history,
         business_intelligence, opportunity, proposal
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("refresh_token_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── businesses ─────────────────────────────────────────────────────
    op.create_table(
        "businesses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255), nullable=False),
        sa.Column("city", sa.String(255), nullable=False),
        sa.Column("country", sa.String(255), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False, server_default=""),
        sa.Column("followers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("engagement_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("website", sa.String(2048), nullable=True),
        sa.Column("instagram", sa.String(2048), nullable=True),
        sa.Column("facebook", sa.String(2048), nullable=True),
        sa.Column("cover_image", sa.String(2048), nullable=False, server_default=""),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("has_online_orders", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("posts_last_30", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_businesses_slug", "businesses", ["slug"], unique=True)
    op.create_index("ix_businesses_category", "businesses", ["category"])

    # ── business_contacts ──────────────────────────────────────────────
    op.create_table(
        "business_contacts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_business_contacts_slug", "business_contacts", ["slug"], unique=True)
    op.create_index("ix_business_contacts_business_id", "business_contacts", ["business_id"])

    # ── search_history ─────────────────────────────────────────────────
    op.create_table(
        "search_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("query", sa.String(2048), nullable=False, server_default=""),
        sa.Column("filters", JSONB(), nullable=False, server_default="{}"),
        sa.Column("result_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_search_history_user_id_created_at", "search_history", ["user_id", "created_at"])

    # ── business_intelligence ──────────────────────────────────────────
    op.create_table(
        "business_intelligence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("business_id", UUID(as_uuid=True), sa.ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("analysis_type", sa.String(50), nullable=False, server_default="deterministic"),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_business_intelligence_business_id", "business_intelligence", ["business_id"])
    op.create_index(
        "ix_business_intelligence_business_id_created",
        "business_intelligence",
        ["business_id", "created_at"],
    )

    # ── opportunity ────────────────────────────────────────────────────
    op.create_table(
        "opportunity",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_intelligence_id",
            UUID(as_uuid=True),
            sa.ForeignKey("business_intelligence.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_opportunity_business_intelligence_id", "opportunity", ["business_intelligence_id"])
    op.create_index(
        "ix_opportunity_business_intelligence_id_created",
        "opportunity",
        ["business_intelligence_id", "created_at"],
    )

    # ── proposal ───────────────────────────────────────────────────────
    op.create_table(
        "proposal",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "opportunity_id",
            UUID(as_uuid=True),
            sa.ForeignKey("opportunity.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("content", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_proposal_opportunity_id", "proposal", ["opportunity_id"])
    op.create_index("ix_proposal_opportunity_id_created", "proposal", ["opportunity_id", "created_at"])


def downgrade() -> None:
    op.drop_table("proposal")
    op.drop_table("opportunity")
    op.drop_table("business_intelligence")
    op.drop_table("search_history")
    op.drop_table("business_contacts")
    op.drop_table("businesses")
    op.drop_table("users")
