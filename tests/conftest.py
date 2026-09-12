# tests/conftest.py

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.role import Role


from tests.factories import UtilisateurDataFactory, EntrepriseDataFactory, ResponsableDataFactory

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        for nom in ["etudiant", "entreprise", "responsable_pedagogique", "admin"]:
            session.add(Role(nom=nom))
        await session.commit()

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def _inscrire_et_connecter(client: AsyncClient, data: dict) -> tuple[str, dict]:

    await client.post("/auth/register", json=data)
    reponse = await client.post(
        "/auth/token",
        data={"username": data["email"], "password": data["mot_de_passe"]},
    )
    return reponse.json()["access_token"], data


@pytest_asyncio.fixture
async def utilisateur_etudiant(client: AsyncClient):
    data = UtilisateurDataFactory()
    token, data = await _inscrire_et_connecter(client, data)
    return {"token": token, "data": data}


@pytest_asyncio.fixture
async def utilisateur_entreprise(client: AsyncClient):
    data = EntrepriseDataFactory()
    token, data = await _inscrire_et_connecter(client, data)
    return {"token": token, "data": data}


@pytest_asyncio.fixture
async def utilisateur_responsable(client: AsyncClient):
    data = ResponsableDataFactory()
    token, data = await _inscrire_et_connecter(client, data)
    return {"token": token, "data": data}
