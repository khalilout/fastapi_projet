from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.db.session import get_db
from app.models.user import Utilisateur
from app.models.candidature import StatutCandidature as StatutCandidatureModele
from app.repositories.candidature_repository import CandidatureRepository
from app.repositories.entreprise_repository import EntrepriseRepository
from app.repositories.offre_repository import OffreRepository
from app.schemas.candidature import CandidatureOut, CandidatureDecision
from app.core.errors import RessourceNonTrouvee, RegleMetierInvalide
from app.utils.pagination import ParametresPagination, valider_pagination


router = APIRouter(tags=["candidatures"])


@router.post("/offers/{offer_id}/applications", status_code=status.HTTP_201_CREATED, response_model=CandidatureOut)
async def creer_candidature(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("etudiant")),
):
    repo_offre = OffreRepository(db)
    offre = await repo_offre.obtenir_par_id(offer_id)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")

    repo_candidature = CandidatureRepository(db)
    existante = await repo_candidature.obtenir_candidature_active(offer_id, utilisateur.id)
    if existante is not None:
        raise RegleMetierInvalide("Une candidature active existe déjà pour cette offre")

    candidature = await repo_candidature.creer(offre_id=offer_id, etudiant_id=utilisateur.id)
    await db.commit()
    await db.refresh(candidature)
    return candidature


@router.get("/applications/me", response_model=list[CandidatureOut])
async def mes_candidatures(
    pagination: ParametresPagination = Depends(valider_pagination),
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("etudiant")),
):
    repo = CandidatureRepository(db)
    return await repo.lister_par_etudiant(utilisateur.id, skip=pagination.skip, limit=pagination.limit)


@router.get("/offers/{offer_id}/applications", response_model=list[CandidatureOut])
async def candidatures_de_offre(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("entreprise", "responsable_pedagogique")),
):
    repo_offre = OffreRepository(db)
    offre = await repo_offre.obtenir_par_id(offer_id)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")

    if utilisateur.role.nom == "entreprise":
        repo_entreprise = EntrepriseRepository(db)
        entreprise = await repo_entreprise.obtenir_par_utilisateur_id(utilisateur.id)
        if entreprise is None or offre.entreprise_id != entreprise.id:
            raise RessourceNonTrouvee("Offre non trouvée")

    repo_candidature = CandidatureRepository(db)
    return await repo_candidature.lister_par_offre(offer_id)


@router.patch("/applications/{application_id}/decision", response_model=CandidatureOut)
async def decider_candidature(
    application_id: int,
    payload: CandidatureDecision,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("responsable_pedagogique")),
):
    repo = CandidatureRepository(db)
    candidature = await repo.obtenir_par_id(application_id)
    if candidature is None:
        raise RessourceNonTrouvee("Candidature non trouvée")

    nouveau_statut = StatutCandidatureModele(payload.decision.value)
    candidature = await repo.changer_statut(candidature, nouveau_statut)
    await db.commit()
    await db.refresh(candidature)
    return candidature


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def retirer_candidature(
    application_id: int,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("etudiant")),
):
    repo = CandidatureRepository(db)
    candidature = await repo.obtenir_par_id(application_id)
    if candidature is None:
        raise RessourceNonTrouvee("Candidature non trouvée")
    if candidature.etudiant_id != utilisateur.id:
        raise RessourceNonTrouvee("Candidature non trouvée")
    if candidature.statut == StatutCandidatureModele.acceptee:
        raise RegleMetierInvalide("Impossible de retirer une candidature acceptée")

    await repo.supprimer(candidature)
    await db.commit()
