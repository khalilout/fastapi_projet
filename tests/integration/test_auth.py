from httpx import AsyncClient

from tests.factories import UtilisateurDataFactory


class TestRegister:
    async def test_inscription_reussie(self, client: AsyncClient):
        data = UtilisateurDataFactory()
        reponse = await client.post("/auth/register", json=data)
        assert reponse.status_code == 201
        assert "user_id" in reponse.json()

    async def test_email_deja_utilise_refuse(self, client: AsyncClient):
        data = UtilisateurDataFactory()
        await client.post("/auth/register", json=data)
        reponse = await client.post("/auth/register", json=data)
        assert reponse.status_code == 400

    async def test_role_inconnu_refuse(self, client: AsyncClient):
        data = UtilisateurDataFactory(role="role_qui_nexiste_pas")
        reponse = await client.post("/auth/register", json=data)
        assert reponse.status_code == 400

    async def test_entreprise_sans_nom_refusee(self, client: AsyncClient):
        data = {"email": "x@test.com", "mot_de_passe": "azerty123", "role": "entreprise"}
        reponse = await client.post("/auth/register", json=data)
        assert reponse.status_code == 400

    async def test_mot_de_passe_trop_court_rejete(self, client: AsyncClient):
        data = {"email": "y@test.com", "mot_de_passe": "court", "role": "etudiant"}
        reponse = await client.post("/auth/register", json=data)
        assert reponse.status_code == 422


class TestLogin:
    async def test_login_reussi(self, client: AsyncClient):
        data = UtilisateurDataFactory()
        await client.post("/auth/register", json=data)

        reponse = await client.post(
            "/auth/token",
            data={"username": data["email"], "password": data["mot_de_passe"]},
        )
        assert reponse.status_code == 200
        assert "access_token" in reponse.json()
        assert "refresh_token" in reponse.json()

    async def test_mauvais_mot_de_passe_refuse(self, client: AsyncClient):
        data = UtilisateurDataFactory()
        await client.post("/auth/register", json=data)

        reponse = await client.post(
            "/auth/token",
            data={"username": data["email"], "password": "mauvais_mdp"},
        )
        assert reponse.status_code == 401

    async def test_email_inexistant_refuse(self, client: AsyncClient):
        reponse = await client.post(
            "/auth/token",
            data={"username": "inexistant@test.com", "password": "azerty123"},
        )
        assert reponse.status_code == 401


class TestUsersMe:
    async def test_acces_sans_token_refuse(self, client: AsyncClient):
        reponse = await client.get("/users/me")
        assert reponse.status_code == 401

    async def test_acces_avec_token_reussi(self, client: AsyncClient, utilisateur_etudiant):
        token = utilisateur_etudiant["token"]
        reponse = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert reponse.status_code == 200
        assert reponse.json()["role"] == "etudiant"
