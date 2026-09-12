# tests/unit/test_repositories.py

import pytest

from app.repositories.offre_repository import OffreRepository
from app.repositories.candidature_repository import CandidatureRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.offre import OffreCreate, OffreUpdate
from app.models.offre import StatutOffre
from app.models.candidature import StatutCandidature


class TestOffreRepository:
    async def test_creer_et_obtenir_par_id(self, db_session):
        repo = OffreRepository(db_session)
        offre = await repo.creer(
            OffreCreate(titre="Stage X", mission="Mission X", competences_requises="Python"),
            entreprise_id=1,
        )
        await db_session.commit()

        recuperee = await repo.obtenir_par_id(offre.id)
        assert recuperee is not None
        assert recuperee.titre == "Stage X"
        assert recuperee.statut == StatutOffre.brouillon

    async def test_obtenir_par_id_inexistant_renvoie_none(self, db_session):
        repo = OffreRepository(db_session)
        resultat = await repo.obtenir_par_id(99999)
        assert resultat is None

    async def test_mettre_a_jour_partiel(self, db_session):
        repo = OffreRepository(db_session)
        offre = await repo.creer(
            OffreCreate(titre="Ancien titre", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await db_session.commit()

        mise_a_jour = await repo.mettre_a_jour(offre.id, OffreUpdate(titre="Nouveau titre"))
        assert mise_a_jour.titre == "Nouveau titre"
        assert mise_a_jour.mission == "M"  # inchangé

    async def test_supprimer(self, db_session):
        repo = OffreRepository(db_session)
        offre = await repo.creer(
            OffreCreate(titre="À supprimer", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await db_session.commit()

        supprimee = await repo.supprimer(offre.id)
        assert supprimee is True
        assert await repo.obtenir_par_id(offre.id) is None

    async def test_supprimer_inexistant_renvoie_false(self, db_session):
        repo = OffreRepository(db_session)
        assert await repo.supprimer(99999) is False

    async def test_lister_publiees_filtre_bien(self, db_session):
        repo = OffreRepository(db_session)
        brouillon = await repo.creer(
            OffreCreate(titre="Brouillon", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        publiee = await repo.creer(
            OffreCreate(titre="Publiee", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await repo.changer_statut(publiee.id, StatutOffre.publiee)
        await db_session.commit()

        resultat = await repo.lister_publiees()
        titres = [o.titre for o in resultat]
        assert "Publiee" in titres
        assert "Brouillon" not in titres

    async def test_compter_par_statut(self, db_session):
        repo = OffreRepository(db_session)
        await repo.creer(OffreCreate(titre="A", mission="M", competences_requises="C"), entreprise_id=1)
        await repo.creer(OffreCreate(titre="B", mission="M", competences_requises="C"), entreprise_id=1)
        await db_session.commit()

        stats = await repo.compter_par_statut()
        assert stats.get("brouillon", 0) >= 2


class TestCandidatureRepository:
    async def test_creer_et_lister_par_etudiant(self, db_session):
        offre_repo = OffreRepository(db_session)
        offre = await offre_repo.creer(
            OffreCreate(titre="Stage", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await db_session.commit()

        cand_repo = CandidatureRepository(db_session)
        candidature = await cand_repo.creer(offre_id=offre.id, etudiant_id=42)
        await db_session.commit()

        assert candidature.statut == StatutCandidature.en_attente

        mes_candidatures = await cand_repo.lister_par_etudiant(42)
        assert len(mes_candidatures) == 1

    async def test_obtenir_candidature_active(self, db_session):
        offre_repo = OffreRepository(db_session)
        offre = await offre_repo.creer(
            OffreCreate(titre="Stage", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await db_session.commit()

        cand_repo = CandidatureRepository(db_session)
        await cand_repo.creer(offre_id=offre.id, etudiant_id=7)
        await db_session.commit()

        active = await cand_repo.obtenir_candidature_active(offre.id, 7)
        assert active is not None

        aucune = await cand_repo.obtenir_candidature_active(offre.id, 999)
        assert aucune is None

    async def test_changer_statut_et_supprimer(self, db_session):
        offre_repo = OffreRepository(db_session)
        offre = await offre_repo.creer(
            OffreCreate(titre="Stage", mission="M", competences_requises="C"),
            entreprise_id=1,
        )
        await db_session.commit()

        cand_repo = CandidatureRepository(db_session)
        candidature = await cand_repo.creer(offre_id=offre.id, etudiant_id=3)
        await db_session.commit()

        mise_a_jour = await cand_repo.changer_statut(candidature, StatutCandidature.acceptee)
        assert mise_a_jour.statut == StatutCandidature.acceptee

        await cand_repo.supprimer(mise_a_jour)
        await db_session.commit()
        assert await cand_repo.obtenir_par_id(candidature.id) is None


class TestRoleRepository:
    async def test_obtenir_par_nom_existant(self, db_session):
        repo = RoleRepository(db_session)
        role = await repo.obtenir_par_nom("etudiant")
        assert role is not None
        assert role.nom == "etudiant"

    async def test_obtenir_par_nom_inexistant(self, db_session):
        repo = RoleRepository(db_session)
        role = await repo.obtenir_par_nom("role_bidon")
        assert role is None