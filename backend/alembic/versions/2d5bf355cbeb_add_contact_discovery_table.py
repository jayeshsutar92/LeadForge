"""add_contact_discovery_table

Revision ID: 2d5bf355cbeb
Revises: 5476916074b0
Create Date: 2026-08-29 21:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2d5bf355cbeb'
down_revision = '5476916074b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('contact_discovery',
    sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_discovery_business_id'), 'contact_discovery', ['business_id'], unique=False)
    op.create_index('ix_contact_discovery_business_id_created', 'contact_discovery', ['business_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_contact_discovery_id'), 'contact_discovery', ['id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_contact_discovery_id'), table_name='contact_discovery')
    op.drop_index('ix_contact_discovery_business_id_created', table_name='contact_discovery')
    op.drop_index(op.f('ix_contact_discovery_business_id'), table_name='contact_discovery')
    op.drop_table('contact_discovery')
