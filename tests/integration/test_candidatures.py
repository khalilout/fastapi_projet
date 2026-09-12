from httpx import AsyncClient

from tests.factories import OffreDataFactory, EntrepriseDataFactory


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _creer_offre_publiee(client: AsyncClient, token_entreprise: str, token_responsable: str) -> int:
    payload = OffreDataFactory()
    creation = await client.post("/offers/", json=payload, headers=auth_headers(token_entreprise))
    offre_id = creation.json()["id"]

    await client.patch(f"/offers/{offre_id}/submit", headers=auth_headers(token_entreprise))
    await client.patch(
        f"/offers/{offre_id}/review",
        json={"decision": "publish"},
        headers=auth_headers(token_responsable),
    )
    return offre_id


class TestCreationCandidature:
    async def test_etudiant_peut_candidater(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        reponse = await client.post(
            f"/offers/{offre_id}/applications",
            headers=auth_headers(utilisateur_etudiant["token"]),
        )
        assert reponse.status_code == 201
        assert reponse.json()["statut"] == "en_attente"

    async def test_entreprise_ne_peut_pas_candidater(
        self, client: AsyncClient, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        reponse = await client.post(
            f"/offers/{offre_id}/applications",
            headers=auth_headers(utilisateur_entreprise["token"]),
        )
        assert reponse.status_code == 403

    async def test_double_candidature_active_refusee(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        token = utilisateur_etudiant["token"]

        premiere = await client.post(f"/offers/{offre_id}/applications", headers=auth_headers(token))
        assert premiere.status_code == 201

        deuxieme = await client.post(f"/offers/{offre_id}/applications", headers=auth_headers(token))
        assert deuxieme.status_code == 400


class TestDecisionCandidature:
    async def test_responsable_peut_accepter(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        candidature = await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )
        candidature_id = candidature.json()["id"]

        decision = await client.patch(
            f"/applications/{candidature_id}/decision",
            json={"decision": "acceptee"},
            headers=auth_headers(utilisateur_responsable["token"]),
        )
        assert decision.status_code == 200
        assert decision.json()["statut"] == "acceptee"

    async def test_etudiant_ne_peut_pas_decider(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        candidature = await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )
        candidature_id = candidature.json()["id"]

        decision = await client.patch(
            f"/applications/{candidature_id}/decision",
            json={"decision": "acceptee"},
            headers=auth_headers(utilisateur_etudiant["token"]),
        )
        assert decision.status_code == 403


class TestRetraitCandidature:
    async def test_etudiant_peut_retirer_candidature_en_attente(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        candidature = await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )
        candidature_id = candidature.json()["id"]

        retrait = await client.delete(
            f"/applications/{candidature_id}", headers=auth_headers(utilisateur_etudiant["token"])
        )
        assert retrait.status_code == 204

    async def test_impossible_de_retirer_candidature_acceptee(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        candidature = await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )
        candidature_id = candidature.json()["id"]

        await client.patch(
            f"/applications/{candidature_id}/decision",
            json={"decision": "acceptee"},
            headers=auth_headers(utilisateur_responsable["token"]),
        )

        retrait = await client.delete(
            f"/applications/{candidature_id}", headers=auth_headers(utilisateur_etudiant["token"])
        )
        assert retrait.status_code == 400


class TestIsolationEntreprise:

    async def test_entreprise_ne_voit_pas_candidatures_dune_autre_entreprise(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        # Entreprise A crée et publie une offre
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        # Un étudiant y candidate
        await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )

        # Une DEUXIÈME entreprise (B), distincte, tente de voir les candidatures de l'offre de A
        data_entreprise_b = EntrepriseDataFactory()
        await client.post("/auth/register", json=data_entreprise_b)
        login_b = await client.post(
            "/auth/token",
            data={"username": data_entreprise_b["email"], "password": data_entreprise_b["mot_de_passe"]},
        )
        token_entreprise_b = login_b.json()["access_token"]

        reponse = await client.get(
            f"/offers/{offre_id}/applications", headers=auth_headers(token_entreprise_b)
        )
        # Isolation : 404, pas 403 (ne pas révéler l'existence de la ressource)
        assert reponse.status_code == 404

    async def test_entreprise_proprietaire_voit_bien_ses_candidatures(
        self, client: AsyncClient, utilisateur_etudiant, utilisateur_entreprise, utilisateur_responsable
    ):
        offre_id = await _creer_offre_publiee(
            client, utilisateur_entreprise["token"], utilisateur_responsable["token"]
        )
        await client.post(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_etudiant["token"])
        )

        reponse = await client.get(
            f"/offers/{offre_id}/applications", headers=auth_headers(utilisateur_entreprise["token"])
        )
        assert reponse.status_code == 200
        assert len(reponse.json()) == 1
