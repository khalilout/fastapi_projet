import enum
from datetime import datetime
import typing

from sqlalchemy import Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
if typing.TYPE_CHECKING:
    from app.models.offre import Offre
    from app.models.user import Utilisateur


class StatutCandidature(str, enum.Enum):
    en_attente = "en_attente"
    acceptee = "acceptee"
    refusee = "refusee"
    retiree = "retiree"


class Candidature(Base):
    __tablename__ = "candidatures"

    id: Mapped[int] = mapped_column(primary_key=True)
    offre_id: Mapped[int] = mapped_column(ForeignKey("offres.id"))
    etudiant_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"))
    statut: Mapped[StatutCandidature] = mapped_column(
        SAEnum(StatutCandidature, name="statut_candidature_enum"),
        default=StatutCandidature.en_attente,
    )
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    offre: Mapped["Offre"] = relationship(back_populates="candidatures")
    etudiant: Mapped["Utilisateur"] = relationship()
