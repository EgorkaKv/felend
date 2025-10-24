"""add_verification_type_to_email_verifications

Revision ID: 9ce0e3290f23
Revises: 49626bde8086
Create Date: 2025-10-24 18:47:46.309826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ce0e3290f23'
down_revision: Union[str, Sequence[str], None] = '49626bde8086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type
    verification_type_enum = sa.Enum(
        'email_verification', 
        'password_reset', 
        name='verificationtype',
        create_type=True
    )
    verification_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Add verification_type column with default value
    op.add_column(
        'email_verifications',
        sa.Column(
            'verification_type',
            verification_type_enum,
            nullable=False,
            server_default='email_verification'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop column
    op.drop_column('email_verifications', 'verification_type')
    
    # Drop enum type
    sa.Enum(name='verificationtype').drop(op.get_bind(), checkfirst=True)
