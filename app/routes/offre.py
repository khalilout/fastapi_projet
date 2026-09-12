from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.db.session import get_db
from app.models.user import Utilisateur
from app.models.offre import StatutOffre
from app.repositories.offre_repository import OffreRepository
from app.repositories.entreprise_repository import EntrepriseRepository

from app.schemas.offre import OffreCreate, OffreOut, OffreUpdate, OffreReviewDecision
from app.core.errors import RessourceNonTrouvee, RegleMetierInvalide
from app.utils.pagination import ParametresPagination, valider_pagination


router = APIRouter(prefix="/offers", tags=["offres"])


@router.get("/", response_model=list[OffreOut])
async def list_offers(
    pagination: ParametresPagination = Depends(valider_pagination),
    db: AsyncSession = Depends(get_db),
):
    repo = OffreRepository(db)
    return await repo.lister_publiees(skip=pagination.skip, limit=pagination.limit)


@router.get("/{offer_id}", response_model=OffreOut)
async def get_offer(offer_id: int, db: AsyncSession = Depends(get_db)):
    repo = OffreRepository(db)
    offre = await repo.obtenir_par_id(offer_id)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")
    return offre


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OffreOut)
async def create_offer(
    payload: OffreCreate,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("entreprise")),
):
    repo_entreprise = EntrepriseRepository(db)
    entreprise = await repo_entreprise.obtenir_par_utilisateur_id(utilisateur.id)
    if entreprise is None:
        raise RegleMetierInvalide("Aucune fiche entreprise associée à ce compte")

    repo = OffreRepository(db)
    offre = await repo.creer(payload, entreprise_id=entreprise.id)
    await db.commit()
    await db.refresh(offre)
    return offre


@router.patch("/{offer_id}", response_model=OffreOut)
async def update_offer(
    offer_id: int,
    payload: OffreUpdate,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("entreprise", "responsable_pedagogique")),
):
    repo = OffreRepository(db)
    offre = await repo.mettre_a_jour(offer_id, payload)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")
    await db.commit()
    await db.refresh(offre)
    return offre


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("admin")),
):
    repo = OffreRepository(db)
    supprimee = await repo.supprimer(offer_id)
    if not supprimee:
        raise RessourceNonTrouvee("Offre non trouvée")
    await db.commit()


@router.patch("/{offer_id}/submit", response_model=OffreOut)
async def submit_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("entreprise")),
):
    repo = OffreRepository(db)
    offre = await repo.obtenir_par_id(offer_id)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")
    if offre.statut != StatutOffre.brouillon:
        raise RegleMetierInvalide("Seule une offre en brouillon peut être soumise")
    if not offre.titre or not offre.mission or not offre.competences_requises or not offre.entreprise_id:
        raise RegleMetierInvalide("Titre, mission, compétences et entreprise sont obligatoires")

    offre = await repo.changer_statut(offer_id, StatutOffre.soumise)
    await db.commit()
    await db.refresh(offre)
    return offre


@router.patch("/{offer_id}/review", response_model=OffreOut)
async def review_offer(
    offer_id: int,
    payload: OffreReviewDecision,
    db: AsyncSession = Depends(get_db),
    utilisateur: Utilisateur = Depends(require_role("responsable_pedagogique")),
):
    repo = OffreRepository(db)
    offre = await repo.obtenir_par_id(offer_id)
    if offre is None:
        raise RessourceNonTrouvee("Offre non trouvée")
    if offre.statut != StatutOffre.soumise:
        raise RegleMetierInvalide("Seule une offre soumise peut être révisée")

    nouveau_statut = StatutOffre.publiee if payload.decision == "publish" else StatutOffre.refusee
    offre = await repo.changer_statut(offer_id, nouveau_statut)
    await db.commit()
    await db.refresh(offre)
    return offre
