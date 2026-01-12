"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('role', sa.String(20), nullable=False, default='user'),
        sa.Column('plan', sa.String(20), nullable=False, default='free'),
        sa.Column('email_verified_at', sa.DateTime(), nullable=True),
        sa.Column('marketing_opt_in', sa.Boolean(), nullable=False, default=False),
        sa.Column('marketing_opt_in_at', sa.DateTime(), nullable=True),
        sa.Column('unsubscribe_token', sa.String(255), nullable=True, unique=True, index=True),
        sa.Column('unsubscribed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Magic link tokens
    op.create_table(
        'magic_link_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, index=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False, index=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Exchanges
    op.create_table(
        'exchanges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Clusters
    op.create_table(
        'clusters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('exchange_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Labeled addresses
    op.create_table(
        'labeled_addresses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('exchange_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=False),
        sa.Column('chain', sa.String(10), nullable=False, index=True),
        sa.Column('address', sa.String(255), nullable=False, index=True),
        sa.Column('label', sa.String(20), nullable=False),
        sa.Column('cluster_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('clusters.id'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Sync state
    op.create_table(
        'sync_state',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chain', sa.String(10), nullable=False, unique=True, index=True),
        sa.Column('last_processed_block', sa.Integer(), nullable=True),
        sa.Column('last_processed_height', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Raw transfers
    op.create_table(
        'raw_transfers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('timestamp', sa.DateTime(), nullable=False, index=True),
        sa.Column('chain', sa.String(10), nullable=False, index=True),
        sa.Column('tx_hash', sa.String(255), nullable=False, index=True),
        sa.Column('block_number', sa.Integer(), nullable=False, index=True),
        sa.Column('log_index', sa.Integer(), nullable=True),
        sa.Column('from_address', sa.String(255), nullable=False, index=True),
        sa.Column('to_address', sa.String(255), nullable=False, index=True),
        sa.Column('asset_symbol', sa.String(50), nullable=False, index=True),
        sa.Column('asset_address', sa.String(255), nullable=True),
        sa.Column('amount', sa.Numeric(36, 18), nullable=False),
        sa.Column('direction', sa.String(20), nullable=False, index=True),
        sa.Column('exchange_from_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=True, index=True),
        sa.Column('exchange_to_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create indexes for raw_transfers
    op.create_index('idx_raw_transfers_chain_block', 'raw_transfers', ['chain', 'block_number'])
    op.create_index('idx_raw_transfers_asset_timestamp', 'raw_transfers', ['asset_symbol', 'timestamp'])
    
    # Flow metrics
    op.create_table(
        'flow_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('time_bucket', sa.DateTime(), nullable=False, index=True),
        sa.Column('window', sa.String(10), nullable=False),
        sa.Column('exchange_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=True, index=True),
        sa.Column('asset_symbol', sa.String(50), nullable=False, index=True),
        sa.Column('inflow', sa.Numeric(36, 18), nullable=False, default=0),
        sa.Column('outflow', sa.Numeric(36, 18), nullable=False, default=0),
        sa.Column('netflow', sa.Numeric(36, 18), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Alerts
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('exchange_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('exchanges.id'), nullable=True),
        sa.Column('asset_symbol', sa.String(50), nullable=False),
        sa.Column('window', sa.String(10), nullable=False),
        sa.Column('z_score', sa.Numeric(10, 4), nullable=False),
        sa.Column('netflow', sa.Numeric(36, 18), nullable=False),
        sa.Column('baseline_mean', sa.Numeric(36, 18), nullable=False),
        sa.Column('baseline_std', sa.Numeric(36, 18), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), index=True),
    )


def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('flow_metrics')
    op.drop_table('raw_transfers')
    op.drop_table('sync_state')
    op.drop_table('labeled_addresses')
    op.drop_table('clusters')
    op.drop_table('exchanges')
    op.drop_table('magic_link_tokens')
    op.drop_table('users')
