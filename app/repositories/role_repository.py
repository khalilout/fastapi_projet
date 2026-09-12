from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtenir_par_nom(self, nom: str) -> Role | None:
        resultat = await self.db.execute(
            select(Role).where(Role.nom == nom)
        )
        return resultat.scalar_one_or_none()
