from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import Utilisateur
from app.repositories.user_repository import UtilisateurRepository

from app.core.errors import NonAuthentifie, NonAutorise

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Utilisateur:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise NonAuthentifie("Token d'accès invalide")

    repo = UtilisateurRepository(db)
    utilisateur = await repo.obtenir_par_id(int(payload["sub"]))
    if utilisateur is None or not utilisateur.est_actif:
        raise NonAuthentifie("Utilisateur introuvable ou inactif")
    return utilisateur


def require_role(*roles_autorises: str):
    async def verifier(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if utilisateur.role.nom not in roles_autorises:
            raise NonAutorise("Accès non autorisé pour ce rôle")
        return utilisateur
    return verifier
