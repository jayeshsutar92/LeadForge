"""Add business evidence log and verification states

Revision ID: 6a2b4c5d6e7f
Revises: 5c4f6g7h8i9j_add_location_fields_to_discovery_sessions
Create Date: 2026-09-08 15:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6a2b4c5d6e7f'
down_revision = '5c4f6g7h8i9j'

def upgrade() -> None:
    # Add new columns with server_default so existing rows don't break
    op.add_column('businesses', sa.Column('website_status', sa.String(length=50), server_default='NOT_CHECKED', nullable=False))
    op.add_column('businesses', sa.Column('instagram_status', sa.String(length=50), server_default='NOT_CHECKED', nullable=False))
    op.add_column('businesses', sa.Column('facebook_status', sa.String(length=50), server_default='NOT_CHECKED', nullable=False))
    op.add_column('businesses', sa.Column('evidence_log', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=True))
    op.add_column('businesses', sa.Column('evidence_hash', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('businesses', 'evidence_hash')
    op.drop_column('businesses', 'evidence_log')
    op.drop_column('businesses', 'facebook_status')
    op.drop_column('businesses', 'instagram_status')
    op.drop_column('businesses', 'website_status')
