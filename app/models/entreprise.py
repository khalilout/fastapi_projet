import typing

from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if typing.TYPE_CHECKING:
    from app.models.user import Utilisateur
    from app.models.offre import Offre

class Entreprise(Base):
    __tablename__ = "entreprises"

    id: Mapped[int] = mapped_column(primary_key=True)
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"), unique=True)
    nom: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    utilisateur: Mapped["Utilisateur"] = relationship()
    offres: Mapped[list["Offre"]] = relationship(back_populates="entreprise")
