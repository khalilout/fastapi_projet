from httpx import AsyncClient

from tests.factories import OffreDataFactory


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestCreationOffre:
    async def test_entreprise_peut_creer_une_offre(self, client: AsyncClient, utilisateur_entreprise):
        token = utilisateur_entreprise["token"]
        payload = OffreDataFactory()

        reponse = await client.post("/offers/", json=payload, headers=auth_headers(token))
        assert reponse.status_code == 201
        data = reponse.json()
        assert data["statut"] == "brouillon"
        assert data["entreprise_id"] is not None

    async def test_etudiant_ne_peut_pas_creer_offre(self, client: AsyncClient, utilisateur_etudiant):
        token = utilisateur_etudiant["token"]
        payload = OffreDataFactory()

        reponse = await client.post("/offers/", json=payload, headers=auth_headers(token))
        assert reponse.status_code == 403

    async def test_creation_sans_token_refusee(self, client: AsyncClient):
        payload = OffreDataFactory()
        reponse = await client.post("/offers/", json=payload)
        assert reponse.status_code == 401


class TestWorkflowOffre:
    async def test_workflow_complet_submit_puis_review(
        self, client: AsyncClient, utilisateur_entreprise, utilisateur_responsable
    ):
        token_entreprise = utilisateur_entreprise["token"]
        token_responsable = utilisateur_responsable["token"]

        # 1. Créer l'offre (brouillon)
        payload = OffreDataFactory()
        creation = await client.post("/offers/", json=payload, headers=auth_headers(token_entreprise))
        offre_id = creation.json()["id"]
        assert creation.json()["statut"] == "brouillon"

        # 2. Soumettre (brouillon -> soumise)
        submit = await client.patch(f"/offers/{offre_id}/submit", headers=auth_headers(token_entreprise))
        assert submit.status_code == 200
        assert submit.json()["statut"] == "soumise"

        # 3. Réviser (soumise -> publiee)
        review = await client.patch(
            f"/offers/{offre_id}/review",
            json={"decision": "publish"},
            headers=auth_headers(token_responsable),
        )
        assert review.status_code == 200
        assert review.json()["statut"] == "publiee"

    async def test_impossible_de_reviser_une_offre_en_brouillon(
        self, client: AsyncClient, utilisateur_entreprise, utilisateur_responsable
    ):
        token_entreprise = utilisateur_entreprise["token"]
        token_responsable = utilisateur_responsable["token"]

        payload = OffreDataFactory()
        creation = await client.post("/offers/", json=payload, headers=auth_headers(token_entreprise))
        offre_id = creation.json()["id"]

        # Tentative de review directe sans submit -> doit échouer
        review = await client.patch(
            f"/offers/{offre_id}/review",
            json={"decision": "publish"},
            headers=auth_headers(token_responsable),
        )
        assert review.status_code == 400

    async def test_entreprise_ne_peut_pas_reviser(self, client: AsyncClient, utilisateur_entreprise):
        token = utilisateur_entreprise["token"]
        payload = OffreDataFactory()
        creation = await client.post("/offers/", json=payload, headers=auth_headers(token))
        offre_id = creation.json()["id"]

        review = await client.patch(
            f"/offers/{offre_id}/review",
            json={"decision": "publish"},
            headers=auth_headers(token),
        )
        assert review.status_code == 403


class TestListeOffresPubliques:
    async def test_offre_en_brouillon_invisible_publiquement(
        self, client: AsyncClient, utilisateur_entreprise
    ):
        token = utilisateur_entreprise["token"]
        payload = OffreDataFactory()
        await client.post("/offers/", json=payload, headers=auth_headers(token))

        reponse = await client.get("/offers/")
        assert reponse.status_code == 200
        assert reponse.json() == []

    async def test_offre_publiee_visible_publiquement(
        self, client: AsyncClient, utilisateur_entreprise, utilisateur_responsable
    ):
        token_entreprise = utilisateur_entreprise["token"]
        token_responsable = utilisateur_responsable["token"]

        payload = OffreDataFactory()
        creation = await client.post("/offers/", json=payload, headers=auth_headers(token_entreprise))
        offre_id = creation.json()["id"]

        await client.patch(f"/offers/{offre_id}/submit", headers=auth_headers(token_entreprise))
        await client.patch(
            f"/offers/{offre_id}/review",
            json={"decision": "publish"},
            headers=auth_headers(token_responsable),
        )

        reponse = await client.get("/offers/")
        assert reponse.status_code == 200
        assert len(reponse.json()) == 1
