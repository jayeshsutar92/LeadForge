from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20230806_create_proposal_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'proposal',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('opportunity.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer, nullable=False, default=1),
        sa.Column('content', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Index('ix_proposal_opportunity_id_created', 'opportunity_id', 'created_at')
    )

def downgrade():
    op.drop_table('proposal')
