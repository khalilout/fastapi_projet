from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Utilisateur
from app.schemas.auth import UtilisateurCreate


class UtilisateurRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtenir_par_id(self, utilisateur_id: int) -> Utilisateur | None:
        resultat = await self.db.execute(
            select(Utilisateur)
            .options(selectinload(Utilisateur.role))
            .where(Utilisateur.id == utilisateur_id)
        )
        return resultat.scalar_one_or_none()

    async def obtenir_par_email(self, email: str) -> Utilisateur | None:
        resultat = await self.db.execute(
            select(Utilisateur)
            .options(selectinload(Utilisateur.role))
            .where(Utilisateur.email == email)
        )
        return resultat.scalar_one_or_none()

    async def creer(self, data: UtilisateurCreate) -> Utilisateur:
        nouvel_utilisateur = Utilisateur(**data.model_dump())
        self.db.add(nouvel_utilisateur)
        await self.db.flush()
        await self.db.refresh(nouvel_utilisateur)
        return nouvel_utilisateur
