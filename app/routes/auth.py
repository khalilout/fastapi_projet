from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.utils.hashing import hash_password, verify_password
from app.db.session import get_db
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UtilisateurRepository
from app.repositories.entreprise_repository import EntrepriseRepository
from app.schemas.auth import UtilisateurRegister, UtilisateurCreate, Token, TokenRefresh
from app.core.errors import RegleMetierInvalide, NonAuthentifie

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UtilisateurRegister, db: AsyncSession = Depends(get_db)):
    repo_user = UtilisateurRepository(db)
    repo_role = RoleRepository(db)

    if await repo_user.obtenir_par_email(data.email):
        raise RegleMetierInvalide("Email déjà utilisé")

    role = await repo_role.obtenir_par_nom(data.role)
    if role is None:
        raise RegleMetierInvalide("Rôle inconnu")

    if data.role == "entreprise" and not data.nom_entreprise:
        raise RegleMetierInvalide("Le nom de l'entreprise est requis pour ce rôle")

    payload = UtilisateurCreate(
        email=data.email,
        mot_de_passe_hache=hash_password(data.mot_de_passe),
        role_id=role.id,
    )
    utilisateur = await repo_user.creer(payload)

    if data.role == "entreprise":
        assert data.nom_entreprise is not None  # déjà validé plus haut
        repo_entreprise = EntrepriseRepository(db)
        await repo_entreprise.creer(utilisateur_id=utilisateur.id, nom=data.nom_entreprise)

    await db.commit()
    return {"message": "Compte créé avec succès", "user_id": utilisateur.id}


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    repo = UtilisateurRepository(db)
    utilisateur = await repo.obtenir_par_email(form_data.username)

    if not utilisateur or not verify_password(form_data.password, utilisateur.mot_de_passe_hache):
        raise NonAuthentifie("Identifiants incorrects")
    if not utilisateur.est_actif:
        raise RegleMetierInvalide("Compte désactivé")

    access_token = create_access_token(subject=utilisateur.id)
    refresh_token = create_refresh_token(subject=utilisateur.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
async def refresh(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise NonAuthentifie("Token de rafraîchissement invalide")

    repo = UtilisateurRepository(db)
    utilisateur = await repo.obtenir_par_id(int(payload["sub"]))
    if not utilisateur or not utilisateur.est_actif:
        raise NonAuthentifie("Utilisateur introuvable ou inactif")

    return Token(
        access_token=create_access_token(subject=utilisateur.id),
        refresh_token=create_refresh_token(subject=utilisateur.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
