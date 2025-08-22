"""Create tokens table

Revision ID: c9d3e8c222d7
Revises: 342a5d6e5660
Create Date: 2025-08-22 20:03:09.498685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d3e8c222d7'
down_revision: Union[str, Sequence[str], None] = '342a5d6e5660'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'tokens',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('jti', sa.String(), unique=True, index=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index('ix_tokens_jti', 'tokens', ['jti'], unique=True)
    op.create_index('ix_tokens_id', 'tokens', ['id'])


def downgrade() -> None:
    op.drop_index('ix_tokens_jti', table_name='tokens')
    op.drop_index('ix_tokens_id', table_name='tokens')
    op.drop_table('tokens')