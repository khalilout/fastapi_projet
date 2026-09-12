from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.db.session import get_db
from app.models.user import Utilisateur
from app.repositories.offre_repository import OffreRepository
from app.repositories.candidature_repository import CandidatureRepository

router = APIRouter(prefix="/stats", tags=["statistiques"])


@router.get("/")
async def obtenir_statistiques(
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("responsable_pedagogique")),
):
    repo_offre = OffreRepository(db)
    repo_candidature = CandidatureRepository(db)
    return {
        "offres_par_statut": await repo_offre.compter_par_statut(),
        "candidatures_par_statut": await repo_candidature.compter_par_statut(),
    }
