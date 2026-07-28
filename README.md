# Fitler-Test

Application full stack pour extraire les produits et les guides de taille depuis des boutiques Shopify.

## Objectif

Le projet transforme l'exercice en base SaaS exploitable:

- backend FastAPI avec architecture routes -> services -> repositories -> scraper;
- moteur de scraping Python modulaire par stratégies;
- base PostgreSQL en production, SQLite par défaut en local;
- frontend Next.js 15 sobre pour piloter les scrapings, consulter le catalogue et exporter;
- Docker Compose, Dockerfiles et CI GitHub Actions.

## Architecture

```text
User
  |
  v
Cloudflare Pages / Next.js
  |
  v
FastAPI Backend
  |
  +-- Shopify scraper strategies
  +-- PostgreSQL
  +-- Exporters JSON / CSV / XLSX
```

```text
backend/app
  api/routes      Endpoints REST
  services        Cas d'usage applicatifs
  repositories    Accès SQLAlchemy
  scraper         Strategies Shopify/API/HTML/JSON/SizeGuide
  models          Tables SQLAlchemy
  schemas         Contrats Pydantic
  exporters       JSON, CSV, XLSX

frontend/app      Pages Next.js
frontend/components
frontend/services Client API
infra             Docker Compose et reverse proxy
```

## Fonctionnalités

- `POST /scrape`: lance un job de scraping asynchrone via `BackgroundTasks`.
- `GET /jobs/{id}` et `GET /jobs/latest`: suivi des jobs.
- `GET /products` et `GET /products/{id}`: catalogue paginé, triable et recherchable.
- `GET /size-guides`: guides extraits et tables normalisées.
- `GET /export/json`, `/export/csv`, `/export/xlsx`: exports téléchargeables.

Le scraper essaie d'abord `/products.json`, puis les données JSON embarquées et enfin les liens HTML produits. Les guides de taille sont détectés via tables HTML, pages dédiées, accordéons, popups et hooks JavaScript courants.

## Installation locale

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Sur Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

L'interface est disponible sur `http://localhost:3000`, avec l'API par défaut sur `http://localhost:8000`.

## Docker

```bash
docker compose -f infra/docker-compose.yml up --build
```

Services:

- frontend: `http://localhost:3000`
- backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## Variables d'environnement

Backend:

- `SCRAPER_DATABASE_URL`: URL SQLAlchemy, PostgreSQL recommandé en production.
- `SCRAPER_ALLOWED_ORIGINS`: origines CORS JSON.
- `SCRAPER_AUTO_CREATE_TABLES`: création automatique des tables en local.
- `SCRAPER_REQUEST_TIMEOUT_SECONDS`: timeout HTTP du scraper.
- `SCRAPER_MAX_SHOPIFY_PAGES`: limite de pagination Shopify.

Frontend:

- `NEXT_PUBLIC_API_BASE_URL`: URL publique du backend.

## Déploiement

- Frontend: Cloudflare Pages, build `npm run build`, dossier Next.js géré par l'intégration Pages.
- Backend: Docker sur Railway ou Fly.io. FastAPI n'est pas un bon candidat direct pour Cloudflare Workers sans adaptation ASGI spécifique.
- Base de données: Neon PostgreSQL ou Supabase.
- Cache/DNS: Cloudflare.
- CI/CD: `.github/workflows/ci.yml`.

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm run test
npm run build
```

## Captures d'écran

À générer après le premier lancement local depuis:

- Dashboard
- Nouveau scraping
- Produits
- Guides de taille
- Exports

## Choix techniques

- `BackgroundTasks` remplace Celery/ARQ pour garder un MVP simple; la frontière service permet d'ajouter un worker sans réécrire l'API.
- SQLite est le défaut local pour réduire la friction; PostgreSQL est configuré pour Docker et production.
- La logique métier reste hors routes FastAPI et hors composants React.
- Les stratégies de scraping sont indépendantes et testables.
