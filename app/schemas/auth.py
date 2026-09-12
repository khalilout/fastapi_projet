from pydantic import BaseModel, EmailStr, Field


class UtilisateurRegister(BaseModel):
    email: EmailStr
    mot_de_passe: str = Field(min_length=8, max_length=100)
    role: str
    nom_entreprise: str | None = None

class UtilisateurCreate(BaseModel):
    email: EmailStr
    mot_de_passe_hache: str
    role_id: int
    est_actif: bool = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str
