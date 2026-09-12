from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidature import Candidature, StatutCandidature
from sqlalchemy import func


class CandidatureRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def obtenir_par_id(self, candidature_id: int) -> Candidature | None:
        resultat = await self.db.execute(
            select(Candidature).where(Candidature.id == candidature_id)
        )
        return resultat.scalar_one_or_none()

    async def lister_par_etudiant(self, etudiant_id: int, skip: int = 0, limit: int = 100) -> list[Candidature]:
        resultat = await self.db.execute(
            select(Candidature)
            .where(Candidature.etudiant_id == etudiant_id)
            .offset(skip)
            .limit(limit)
        )
        return list(resultat.scalars().all())

    async def lister_par_offre(self, offre_id: int, skip: int = 0, limit: int = 100) -> list[Candidature]:
        resultat = await self.db.execute(
            select(Candidature)
            .where(Candidature.offre_id == offre_id)
            .offset(skip)
            .limit(limit)
        )
        return list(resultat.scalars().all())
        

    async def obtenir_candidature_active(self, offre_id: int, etudiant_id: int) -> Candidature | None:
        resultat = await self.db.execute(
            select(Candidature).where(
                Candidature.offre_id == offre_id,
                Candidature.etudiant_id == etudiant_id,
                Candidature.statut.in_([StatutCandidature.en_attente, StatutCandidature.acceptee]),
            )
        )
        return resultat.scalar_one_or_none()

    async def creer(self, offre_id: int, etudiant_id: int) -> Candidature:
        candidature = Candidature(offre_id=offre_id, etudiant_id=etudiant_id)
        self.db.add(candidature)
        await self.db.flush()
        await self.db.refresh(candidature)
        return candidature

    async def changer_statut(self, candidature: Candidature, nouveau_statut: StatutCandidature) -> Candidature:
        candidature.statut = nouveau_statut
        await self.db.flush()
        await self.db.refresh(candidature)
        return candidature

    async def supprimer(self, candidature: Candidature) -> None:
        await self.db.delete(candidature)
        await self.db.flush()

    async def compter_par_statut(self) -> dict[str, int]:
        resultat = await self.db.execute(
            select(Candidature.statut, func.count(Candidature.id)).group_by(Candidature.statut)
        )
        return {statut.value: count for statut, count in resultat.all()}
