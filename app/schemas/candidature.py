from enum import Enum
from pydantic import BaseModel


class StatutCandidature(str, Enum):
    en_attente = "en_attente"
    acceptee = "acceptee"
    refusee = "refusee"
    retiree = "retiree"


class CandidatureDecision(BaseModel):
    decision: StatutCandidature


class CandidatureOut(BaseModel):
    id: int
    offre_id: int
    etudiant_id: int
    statut: StatutCandidature