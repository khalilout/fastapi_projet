
## Choix d'architecture et de modélisation

**Domaines multiples (`<domaine>.py`)** : l'arborescence impose un pattern générique
`<domaine>.py` par entité métier. StageFlow en compte trois : `offre`, `candidature`
et `entreprise` — chacun décliné en fichier propre dans `models/`, `schemas/` et
`repositories/`, pour respecter la séparation des responsabilités exigée.

**Table `Entreprise` séparée du rôle** : le rôle `entreprise` gère les *permissions*,
mais une entreprise est une *entité métier* à part entière (nom, description),
distincte du compte qui s'y connecte. Cette séparation est nécessaire pour respecter
deux règles du sujet : une offre doit être rattachée à une entreprise précise
(`Offre.entreprise_id`), et une entreprise ne doit voir que les candidatures de
*ses* offres — isolation qui repose sur la comparaison entre entreprises, pas sur
l'identifiant utilisateur. La table `entreprises` est liée en 1-à-1 à `utilisateurs`.



# StageFlow — API de gestion sécurisée des stages data

API interne permettant de suivre les offres de stage,
les candidatures, les validations pédagogiques et les avis des encadrants.

## Rôles et habilitations

- **etudiant** : consulte les offres publiées, candidate, suit ses candidatures, retire une candidature tant qu'elle n'est pas acceptée.
- **entreprise** : crée des offres en brouillon, les soumet, consulte les candidatures de ses propres offres uniquement.
- **responsable_pedagogique** : publie/refuse une offre, accepte/refuse une candidature, consulte les statistiques globales.
- **admin** : gère les comptes (suppression d'offres).

## Prérequis

- Python 3.11+
- PostgreSQL 16+ (ou Docker)
- Docker Desktop (optionnel, pour lancer via docker-compose)

## Installation locale

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt   # pour lint/tests (ruff, mypy, aiosqlite...)
```

## Variables d'environnement

Créer un fichier `.env` à la racine avec :
DATABASE_URL=postgresql+asyncpg://stageflow_user:stageflow_pass@localhost:5432/stageflow_db
SECRET_KEY=une-cle-secrete-longue-et-aleatoire
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7


## Lancer les migrations

```bash
alembic upgrade head
```

## Lancement en développement

```bash
fastapi dev app/main.py
```

API sur `http://127.0.0.1:8000`, documentation interactive sur `http://127.0.0.1:8000/docs`.

## Lancement avec Docker

```bash
docker compose up --build
```

Les migrations Alembic s'appliquent automatiquement au démarrage du conteneur `api`.

## Lancer les tests

```bash
pytest -v
```

Avec couverture de code :

```bash
pytest --cov=app --cov-report=term-missing
```

Les tests utilisent une base SQLite en mémoire, isolée de la base PostgreSQL de développement/production.

## Qualité du code

```bash
ruff check app/ tests/
mypy app/
```

## Endpoints principaux

| Méthode | Route | Rôle requis |
|---|---|---|
| POST | `/auth/register` | public |
| POST | `/auth/token` | public |
| POST | `/auth/refresh` | public |
| GET | `/users/me` | authentifié |
| GET | `/offers/` | public (offres publiées uniquement) |
| POST | `/offers/` | entreprise |
| PATCH | `/offers/{id}/submit` | entreprise |
| PATCH | `/offers/{id}/review` | responsable_pedagogique |
| POST | `/offers/{id}/applications` | etudiant |
| GET | `/applications/me` | etudiant |
| GET | `/offers/{id}/applications` | entreprise, responsable_pedagogique |
| PATCH | `/applications/{id}/decision` | responsable_pedagogique |
| DELETE | `/applications/{id}` | etudiant |
| GET | `/stats/` | responsable_pedagogique |

## Architecture

app/
├── main.py
├── routes/ # auth, users, offre, candidature, stats
├── core/ # config, security (JWT/hash), permissions, errors
├── db/ # session, base SQLAlchemy
├── models/ # entités SQLAlchemy (user, role, entreprise, offre, candidature)
├── schemas/ # DTO Pydantic (entrée/sortie)
├── repositories/ # accès données, aucune route n'appelle SQLAlchemy directement
├── middlewares/ # request_id, security_headers
└── utils/ # hashing, pagination, time


