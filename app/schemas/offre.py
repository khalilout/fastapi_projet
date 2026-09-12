from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Literal

class OffreReviewDecision(BaseModel):
    decision: Literal["publish", "reject"]


class StatutOffre(str, Enum):
    brouillon = "brouillon"
    soumise = "soumise"
    publiee = "publiee"
    refusee = "refusee"


class OffreCreate(BaseModel):
    titre: str
    mission: str
    competences_requises: str

    @field_validator("titre")
    @classmethod
    def titre_non_vide(cls, valeur: str) -> str:
        if not valeur.strip():
            raise ValueError("Le titre ne peut pas être vide")
        return valeur.strip()


class OffreUpdate(BaseModel):
    titre: str | None = None
    mission: str | None = None
    competences_requises: str | None = None
    # statut: StatutOffre | None = None



class OffreOut(BaseModel):
    id: int
    titre: str
    mission: str
    competences_requises: str
    entreprise_id: int | None = None
    statut: StatutOffre
