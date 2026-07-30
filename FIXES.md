# Rapport de corrections — Fitler Test

## Problème principal : frontend appelle `localhost:8000` en production

### Symptôme
```
POST http://localhost:8000/scrape net::ERR_CONNECTION_REFUSED
GET  http://localhost:8000/products?page_size=1 net::ERR_CONNECTION_REFUSED
```
Le frontend déployé sur Cloudflare Pages tentait de joindre `localhost:8000`
au lieu de `https://fitler-test.onrender.com`.

---

## Corrections appliquées

### 1. `frontend/services/api.ts` — URL hardcodée ignorait la variable d'env

**Avant**
```ts
export const API_BASE_URL = "https://fitler-test.onrender.com";
```

**Après**
```ts
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://fitler-test.onrender.com";
```

**Pourquoi** : Next.js embarque les variables `NEXT_PUBLIC_*` au moment du build.
Si la variable n'est pas définie lors du build Cloudflare Pages, le fallback
`"https://fitler-test.onrender.com"` prend le relais. L'ancienne version
hardcodait l'URL mais le build déployé sur Cloudflare était une version
antérieure qui contenait encore `localhost:8000`.

**Action requise** : dans Cloudflare Pages → Settings → Environment variables,
ajouter :
```
NEXT_PUBLIC_API_BASE_URL = https://fitler-test.onrender.com
```
Puis redéployer (nouveau commit ou "Retry deployment").

---

### 2. `backend/app/main.py` — imports `Depends` dupliqués

**Avant**
```python
from fastapi import FastAPI
...
from fastapi import Depends          # doublon 1
# Modification pour la vérification...
from fastapi import Depends          # doublon 2
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_session
```

**Après**
```python
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_session
```

**Pourquoi** : imports redondants, commentaire de travail laissé en prod.
Aucun impact fonctionnel mais code sale et trompeur.

---

### 3. `infra/docker-compose.yml` — trois problèmes

#### 3a. Préfixe `SCRAPER_` manquant sur `DATABASE_URL`

**Avant**
```yaml
DATABASE_URL: postgresql://...neon.tech/...
```

**Après**
```yaml
SCRAPER_DATABASE_URL: ${SCRAPER_DATABASE_URL:-postgresql://postgres:postgres@postgres:5432/shopify_scraper}
```

**Pourquoi** : `pydantic-settings` lit `SCRAPER_DATABASE_URL` (préfixe défini
dans `config.py`). Sans le préfixe, la variable était ignorée et le backend
tombait sur SQLite en local ou échouait en prod.

#### 3b. Credentials en clair dans le fichier versionné

**Avant**
```yaml
DATABASE_URL: postgresql://neondb_owner:npg_AnN8Ebd7upSC@ep-weathered-star-ay82lbbz...
```

**Après**
```yaml
SCRAPER_DATABASE_URL: ${SCRAPER_DATABASE_URL:-postgresql://postgres:postgres@postgres:5432/shopify_scraper}
```

**Pourquoi** : les credentials Neon étaient commités en clair dans le dépôt.
Ils sont maintenant injectés via variable d'environnement avec un fallback
local sûr.

#### 3c. `NEXT_PUBLIC_API_BASE_URL` pointait vers `localhost:8000`

**Avant**
```yaml
NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
```

**Après**
```yaml
NEXT_PUBLIC_API_BASE_URL: ${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}
```

**Pourquoi** : en Docker local le backend est accessible via le nom de service
`backend:8000`, pas `localhost:8000`. La valeur par défaut reste correcte pour
le dev local, et en prod la variable est surchargée.

---

## Résumé des fichiers modifiés

| Fichier | Type de correction |
|---|---|
| `frontend/services/api.ts` | Variable d'env au lieu de hardcode |
| `backend/app/main.py` | Suppression imports dupliqués |
| `infra/docker-compose.yml` | Préfixe SCRAPER_, secrets via env, URL frontend |

---

## Action requise pour finaliser le déploiement

1. **Cloudflare Pages** → Settings → Environment variables :
   ```
   NEXT_PUBLIC_API_BASE_URL = https://fitler-test.onrender.com
   ```
2. Pousser ce commit sur `main` pour déclencher le rebuild Cloudflare.
3. **Render** → vérifier que `SCRAPER_ALLOWED_ORIGINS` contient bien le domaine
   Cloudflare Pages final (ex: `["https://fitler-test.pages.dev"]`).
4. Révoquer et régénérer les credentials Neon (ils ont été commités en clair).
