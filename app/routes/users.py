from fastapi import APIRouter, Depends

from app.core.permissions import get_current_user
from app.models.user import Utilisateur

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def read_me(utilisateur: Utilisateur = Depends(get_current_user)):
    return {
        "id": utilisateur.id,
        "email": utilisateur.email,
        "role": utilisateur.role.nom,
        "est_actif": utilisateur.est_actif,
    }
