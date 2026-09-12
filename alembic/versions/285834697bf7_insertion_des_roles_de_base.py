"""insertion des roles de base

Revision ID: 285834697bf7
Revises: 19c8332693ca
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '285834697bf7'
down_revision: Union[str, Sequence[str], None] = '19c8332693ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Integer),
        sa.column("nom", sa.String),
    )

    op.bulk_insert(
        roles_table,
        [
            {"nom": "etudiant"},
            {"nom": "entreprise"},
            {"nom": "responsable_pedagogique"},
            {"nom": "admin"},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM roles WHERE nom IN "
        "('etudiant', 'entreprise', 'responsable_pedagogique', 'admin')"
    )