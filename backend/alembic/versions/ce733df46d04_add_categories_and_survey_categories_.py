"""add_categories_and_survey_categories_tables

Revision ID: ce733df46d04
Revises: 380e4bff066b
Create Date: 2025-10-29 01:30:58.720661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce733df46d04'
down_revision: Union[str, Sequence[str], None] = '380e4bff066b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
