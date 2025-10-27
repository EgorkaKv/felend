"""add_user_data_to_email_verifications

Revision ID: c2c2407b044c
Revises: 9ce0e3290f23
Create Date: 2025-10-27 22:39:38.144218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2c2407b044c'
down_revision: Union[str, Sequence[str], None] = '9ce0e3290f23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Сделать user_id nullable
    op.alter_column('email_verifications', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    
    # Добавить поля для хранения данных пользователя
    op.add_column('email_verifications', 
                  sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('email_verifications', 
                  sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.add_column('email_verifications', 
                  sa.Column('full_name', sa.String(length=255), nullable=True))
    
    # Создать индекс на email
    op.create_index(op.f('ix_email_verifications_email'), 'email_verifications', ['email'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Удалить индекс
    op.drop_index(op.f('ix_email_verifications_email'), table_name='email_verifications')
    
    # Удалить добавленные колонки
    op.drop_column('email_verifications', 'full_name')
    op.drop_column('email_verifications', 'hashed_password')
    op.drop_column('email_verifications', 'email')
    
    # Вернуть user_id NOT NULL
    op.alter_column('email_verifications', 'user_id',
                    existing_type=sa.INTEGER(),
                    nullable=False)
