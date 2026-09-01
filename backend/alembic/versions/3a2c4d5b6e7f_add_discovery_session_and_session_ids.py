"""Add DiscoverySession and session_ids

Revision ID: 3a2c4d5b6e7f
Revises: 2d5bf355cbeb
Create Date: 2026-09-01 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '3a2c4d5b6e7f'
down_revision: Union[str, None] = '2d5bf355cbeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create discovery_sessions table
    op.create_table('discovery_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('query', sa.String(length=255), nullable=False),
        sa.Column('region', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_discovery_sessions_user_id', 'discovery_sessions', ['user_id'], unique=False)
    
    # Add discovery_session_ids to businesses
    op.add_column('businesses', sa.Column('discovery_session_ids', sa.JSON(), nullable=False, server_default='[]'))
    
    # Add discovery_session_ids to leads
    op.add_column('leads', sa.Column('discovery_session_ids', sa.JSON(), nullable=False, server_default='[]'))


def downgrade() -> None:
    op.drop_column('leads', 'discovery_session_ids')
    op.drop_column('businesses', 'discovery_session_ids')
    op.drop_index('ix_discovery_sessions_user_id', table_name='discovery_sessions')
    op.drop_table('discovery_sessions')
