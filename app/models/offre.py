import enum
from datetime import datetime
import typing

from sqlalchemy import String, Text, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
if typing.TYPE_CHECKING:
    from app.models.entreprise import Entreprise
    from app.models.candidature import Candidature

class StatutOffre(str, enum.Enum):
    brouillon = "brouillon"
    soumise = "soumise"
    publiee = "publiee"
    refusee = "refusee"


class Offre(Base):
    __tablename__ = "offres"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(255))
    mission: Mapped[str] = mapped_column(Text)
    competences_requises: Mapped[str] = mapped_column(Text)
    entreprise_id: Mapped[int] = mapped_column(ForeignKey("entreprises.id"), nullable=True)
    statut: Mapped[StatutOffre] = mapped_column(
        SAEnum(StatutOffre, name="statut_offre_enum"),
        default=StatutOffre.brouillon,
    )
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    entreprise: Mapped["Entreprise"] = relationship(back_populates="offres")
    candidatures: Mapped[list["Candidature"]] = relationship(back_populates="offre")
