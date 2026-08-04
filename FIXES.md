# Rapport d'analyse et corrections

## Problème principal

Le frontend déployé sur **Cloudflare Workers** continuait d'appeler `http://localhost:8000` au lieu de `https://fitler-test.onrender.com`, rendant l'API inaccessible.

```
POST http://localhost:8000/scrape net::ERR_CONNECTION_REFUSED
GET http://localhost:8000/products?page_size=1 net::ERR_CONNECTION_REFUSED
```

## Analyse de la cause racine

### 1. Build stale avec localhost hardcodé

Le répertoire `.open-next/` (build OpenNext pour Cloudflare) datait du **29/07/2026** et contenait dans le JS minifié :

```js
// ANCIEN build (stale)
let r=null!=(n=null==(s=t(5704).env.NEXT_PUBLIC_API_BASE_URL)?void 0:s.replace(/\/$/,""))?n:"http://localhost:8000";
```

**Cause** : Le `fallback` de la variable d'env était `"http://localhost:8000"` dans l'ancienne version du code source, et le build n'avait jamais été regénéré après la correction.

### 2. `.open-next/` non commité ET non régénéré

- `.open-next/` n'était **pas dans `.gitignore`**, mais il n'était **pas commité non plus** (`git ls-files` retourne vide)
- Le `package.json` avait `"build": "next build"` qui ne génère que `.next/`, pas `.open-next/`
- Cloudflare ne pouvait donc pas rebuild le `.open-next/worker.js` — il utilisait une version obsolète

### 3. Variables d'env Cloudflare mal configurées

- Le `vars` dans `wrangler.jsonc` définit des variables **runtime**, pas **build-time**
- `NEXT_PUBLIC_*` sont substituées par Next.js **au moment du build**, pas au runtime
- Il fallait soit `.env.production` commité, soit la variable définie dans l'environnement de build Cloudflare

### 4. Erreurs supplémentaires découvertes

| Problème | Fichier | Correction |
|----------|---------|------------|
| Driver PostgreSQL incompatible | `session.py` | `postgresql://` → `postgresql+psycopg://` pour psycopg3 |
| Connexion Neon en IPv6 | Render + Neon | Utiliser l'URL **pooler** Neon (`-pooler`) au lieu de la connexion directe |
| Variables Render sans préfixe `SCRAPER_` | Render Dashboard | Renommer `DATABASE_URL` → `SCRAPER_DATABASE_URL`, etc. |
| Titre du commit contenant un fichier backend | `git` | Commit mixte frontend + backend |

## Corrections appliquées

### Frontend (5 fichiers)

| Fichier | Correction |
|---------|------------|
| `frontend/services/api.ts` | Fallback mis à jour : `"http://localhost:8000"` → `"https://fitler-test.onrender.com"` |
| `frontend/.env.production` | **Nouveau fichier** commité : `NEXT_PUBLIC_API_BASE_URL=https://fitler-test.onrender.com` |
| `frontend/wrangler.jsonc` | Ajout de `NEXT_PUBLIC_API_BASE_URL` dans `vars` |
| `frontend/package.json` | Ajout du script `build:cf` : `opennextjs-cloudflare build` |
| `.gitignore` | Ajout de `!.env.production` (exception) + `.open-next/` (ignoré) |

### Backend (1 fichier)

| Fichier | Correction |
|---------|------------|
| `backend/app/db/session.py` | Résolution automatique du driver psycopg3 : toute URL `postgresql://` est convertie en `postgresql+psycopg://` |

## Résultat après rebuild

Le nouveau build contient l'URL correcte, **directement inline** dans le JS :

```js
// NOUVEAU build (corrigé)
let n="https://fitler-test.onrender.com";
```

✅ Plus de `process.env.NEXT_PUBLIC_API_BASE_URL` au runtime — la valeur est gravée dans le bundle.

## Déploiement

```bash
git add .
git commit -m "fix: rebuild OpenNext avec l'URL Render + build CF script"
git push
```

Cloudflare Workers va automatiquement rebuild avec la bonne URL.

## Vérifications manuelles restantes

1. **Render** : Vérifier que les variables d'env utilisent le préfixe `SCRAPER_` :
   - `SCRAPER_DATABASE_URL` (avec l'URL pooler Neon, pas direct)
   - `SCRAPER_ALLOWED_ORIGINS` = `["https://fitler-test.ibra-so-sow.workers.dev","http://localhost:3000"]`
   - `SCRAPER_AUTO_CREATE_TABLES` = `true`

2. **Cloudflare** : Vérifier que le build utilise `npm run build` (qui génère `.next/`) suivi de `npx opennextjs-cloudflare build` (qui génère `.open-next/`)

3. **Neon** : Utiliser l'URL **pooler** (avec `-pooler` dans le hostname) pour éviter le problème IPv4/IPv6

---

## Incident #2 : HTTP 429 sur les scraping en production (02/08/2026)

### Symptôme

Sur Render, les scraping de `kleman-france.com` et `www.andre.fr` échouaient en
HTTP **429** avec un body `local_rate_limited` et un header `server: cloudflare`.

### Diagnostic

- Le 429 ne venait **pas de l'IP Render** : `curl.exe` et `curl_cffi` passaient en
  200 depuis la même machine que httpx (qui faisait 429).
- La cause racine est l'**empreinte TLS (JA3)** : Cloudflare classe httpx/requests
  comme clients non-navigateurs et renvoie un faux 429 anti-bot.
- Les réponses Cloudflare portaient `retry-after: 60` → le retry tenacity attendait
  60 s et dépassait le timeout des jobs.

### Correction (`backend/`)

| Fichier | Correction |
|---------|------------|
| `requirements.txt` | `httpx` → `curl_cffi==0.16.0` |
| `app/scraper/http.py` | Réécrit avec `Session(impersonate="chrome")`, headers navigateur complets, retry tenacity sur erreurs réseau/429, `_retry_wait` plafonné à 20 s (respecte `Retry-After`) |
| `app/core/errors.py` | Ajout de `RateLimitedError(FetchError)` avec `retry_after` |
| `app/core/config.py` | Ajout de `proxy_url` optionnel (`SCRAPER_PROXY_URL`) |
| `app/scraper/client.py` | Erreurs de guide de taille → warning (le job ne échoue plus) |
| `app/scraper/strategies/size_guide.py` | Home en 429 → `[]` sans échouer le job |

### Résultat vérifié en production (Render)

| Boutique | Produits | Variantes | Guides |
|----------|----------|-----------|--------|
| kleman-france.com | 228 | 1 866 | 8 |
| www.andre.fr | 1 648 | 7 721 | 0 |

Base prod : **2 320 produits** / 10 guides, endpoints `/products`, `/size-guides`,
`/jobs/latest` OK.

---

## Incident #3 : build Cloudflare Workers en échec (04/08/2026)

### Symptôme

Le build de `fitler-test` (Workers & Pages, dépôt `Yros-So/Fitler-Test`, branche
`main`, racine `/frontend`) échouait à l'étape `npm ci` avec :

```
npm error code EUSAGE
npm error `npm ci` can only install packages when your package.json and
package-lock.json ... are in sync.
npm error Invalid: lock file's @emnapi/wasi-threads@1.2.1 does not satisfy
@emnapi/wasi-threads@1.2.3
npm error Missing: @emnapi/core@1.10.0 from lock file
```

### Diagnostic

- `package-lock.json` était **désynchronisé** : dépendance transitive
  `@emnapi/wasi-threads@1.2.1` (via `unrs-resolver`) alors que le graphe exige
  `1.2.3`, et `@emnapi/core@1.10.0` absent du lock.
- Cloudflare a mis à jour son npm (≥ 11) qui **valide strictement** la synchro
  lock ↔ `package.json` ; les builds précédents passaient car l'ancien npm était
  permissif. Le CI GitHub (`npm install`) ne détecte pas ce problème, d'où des
  checks verts malgré un build Cloudflare cassé.

### Correction (`frontend/`)

| Fichier | Correction |
|---------|------------|
| `package-lock.json` | Régénéré avec `npm install` (emnapi 1.2.3 / core 1.10.0 présents) ; `npm ci --dry-run` OK |
| `package.json` | Ajout du champ `allowScripts` (`esbuild`, `unrs-resolver`, `workerd`) : politique npm ≥ 11.4 « install scripts » — le `.npmrc` `allow-scripts` est rejeté en install projet, c'est `package.json#allowScripts` qu'il faut |

### À noter

- Le lock généré par opennextjs-cloudflare dans `.open-next/server-functions`
  hérite du lock racine : la régénération corrige aussi l'install interne.
- Vérifier dans le dashboard Cloudflare que le build suivant cible le bon SHA
  (l'intégration GitHub peut rester sur un ancien ref ; un nouveau push force la
  synchro du webhook).
