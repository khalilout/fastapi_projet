from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offre import Offre
from app.schemas.offre import OffreCreate, OffreUpdate


class OffreRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def lister_toutes(self, skip: int = 0, limit: int = 100) -> list[Offre]:
        resultat = await self.db.execute(
            select(Offre).offset(skip).limit(limit)
        )
        return list(resultat.scalars().all())

    async def obtenir_par_id(self, offre_id: int) -> Offre | None:
        resultat = await self.db.execute(
            select(Offre).where(Offre.id == offre_id)
        )
        return resultat.scalar_one_or_none()

    async def creer(self, data: OffreCreate, entreprise_id: int) -> Offre:
        nouvelle_offre = Offre(**data.model_dump(), entreprise_id=entreprise_id)
        self.db.add(nouvelle_offre)
        await self.db.flush()
        await self.db.refresh(nouvelle_offre)
        return nouvelle_offre

    async def mettre_a_jour(self, offre_id: int, data: OffreUpdate) -> Offre | None:
        offre = await self.obtenir_par_id(offre_id)
        if offre is None:
            return None

        donnees_modifiees = data.model_dump(exclude_none=True)
        for champ, valeur in donnees_modifiees.items():
            setattr(offre, champ, valeur)

        await self.db.flush()
        await self.db.refresh(offre)
        return offre

    async def supprimer(self, offre_id: int) -> bool:
        offre = await self.obtenir_par_id(offre_id)
        if offre is None:
            return False
        await self.db.delete(offre)
        await self.db.flush()
        return True

    async def changer_statut(self, offre_id: int, nouveau_statut) -> "Offre | None":
        offre = await self.obtenir_par_id(offre_id)
        if offre is None:
            return None
        offre.statut = nouveau_statut
        await self.db.flush()
        await self.db.refresh(offre)
        return offre

    async def compter_par_statut(self) -> dict[str, int]:
        resultat = await self.db.execute(
            select(Offre.statut, func.count(Offre.id)).group_by(Offre.statut)
        )
        return {statut.value: count for statut, count in resultat.all()}


    async def lister_publiees(self, skip: int = 0, limit: int = 100) -> list[Offre]:
        from app.models.offre import StatutOffre
        resultat = await self.db.execute(
            select(Offre)
            .where(Offre.statut == StatutOffre.publiee)
            .offset(skip)
            .limit(limit)
        )
        return list(resultat.scalars().all())
