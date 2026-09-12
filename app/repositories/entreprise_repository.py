from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entreprise import Entreprise


class EntrepriseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtenir_par_utilisateur_id(self, utilisateur_id: int) -> Entreprise | None:
        resultat = await self.db.execute(
            select(Entreprise).where(Entreprise.utilisateur_id == utilisateur_id)
        )
        return resultat.scalar_one_or_none()

    async def creer(self, utilisateur_id: int, nom: str) -> Entreprise:
        entreprise = Entreprise(utilisateur_id=utilisateur_id, nom=nom)
        self.db.add(entreprise)
        await self.db.flush()
        await self.db.refresh(entreprise)
        return entreprise
