from enum import Enum
from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    etudiant = "etudiant"
    entreprise = "entreprise"
    responsable_pedagogique = "responsable_pedagogique"
    admin = "admin"


class UtilisateurCreate(BaseModel):
    email: EmailStr
    mot_de_passe: str
    role: RoleEnum


class UtilisateurOut(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    est_actif: bool
