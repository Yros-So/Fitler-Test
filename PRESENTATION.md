# Shopify Catalog Extractor — Support de présentation

> Support complet pour la soutenance : trame slide par slide (5–10 min), scénario
> de démo, chiffres live, difficultés et Q&A anticipé.
> Captures d'écran de la démo : [`docs/presentation/`](docs/presentation/).

---

## 1. Infos pratiques

| | |
|---|---|
| **Projet** | Shopify Catalog Extractor — extraction produits + guides de taille de boutiques Shopify |
| **Repo de livraison** | `github.com/Yros-So/shopify-catalog-extractor` |
| **Frontend (démo)** | https://fitler-test.ibra-so-sow.workers.dev |
| **API backend** | https://fitler-test.onrender.com |
| **Docs API (Swagger)** | https://fitler-test.onrender.com/docs |
| **Stack** | Next.js 15 / FastAPI (Python 3.12) / PostgreSQL Neon / Cloudflare Workers / Render / GitHub Actions |

### Chiffres live (au moment de la soutenance)

| Boutique | Produits | Détail |
|---|---|---|
| www.andre.fr | 1 842 | 2 scopes (1 648 + 194) |
| grimfrost.com | 250 | |
| kleman-france.com | 228 | dont guide de taille (8 détectés) |
| minuitsurterre.com | 167 | 2 scopes (53 + 114) |
| **Total** | **2 487 produits** | **12 guides de taille** |

---

## 2. Pitch (30 s — à dire d'abord)

> « Shopify Catalog Extractor est une application full-stack qui récupère
> automatiquement les **catalogues produits et les guides de taille** depuis des
> boutiques Shopify, les normalise dans une base PostgreSQL, et les expose via
> une **API REST** et une **interface web**. Elle est conçue comme un mini-SaaS :
> scraping asynchrone, stratégies de repli, exports JSON/CSV/XLSX, CI/CD, et
> déployée en production sur Cloudflare + Render. »

---

## 3. Trame slide par slide (5–10 min)

### Slide 1 — Contexte & objectif (0:30)
- Sujet : transformer l'exercice d'extraction de catalogues en **base SaaS exploitable**.
- Objectifs : scraping robuste, API propre, UI de pilotage, production réelle.

### Slide 2 — Pitch produit (0:45)
- Le problème : extraire des catalogues e-commerce à la main = fragile et non réutilisable.
- La solution : un moteur de scraping **par stratégies** + une API + une UI.
- `POST /scrape` → job asynchrone → produits + guides normalisés en base.

### Slide 3 — Architecture (1:30)
```
Next.js (Cloudflare Workers) ──> FastAPI ──> moteur de scraping ──> PostgreSQL (Neon)
      UI + exports                  routes→services→repositories      JSON/CSV/XLSX
```
- Backend **FastAPI typé**, layering clair : `routes` → `services` → `repositories` → `scraper`.
- Moteur de scraping en **stratégies indépendantes** (voir §5).
- Upsert par `handle` : idempotent, un re-scrap met à jour sans dupliquer.

### Slide 4 — Démo en direct (2:00) ★ la plus importante
Scénario complet au §4. Montrer, dans l'ordre : dashboard → scraping kleman →
suivi du job → produits (filtre, tri) → fiche produit (variantes/tailles) →
guides de taille → export CSV. Terminer sur le Swagger `/docs`.

### Slide 5 — Fonctionnalités clés (1:00)
- **API REST** : `POST /scrape` (202), `GET /jobs/{id}`, `GET /products` (pagination,
  recherche, tri contraint par regex), `GET /size-guides`, `GET /export/{json,csv,xlsx}`.
- **Variantes** : SKU, prix, disponibilité, options (pointure, taille, couleur).
- **UI Next.js** : dashboard, formulaire de scraping, catalogue, guides, exports.

### Slide 6 — Difficultés rencontrées & solutions (1:30)
1. **Frontend appelait `localhost` en prod** → URL de l'API **gravée au build**
   (`NEXT_PUBLIC_API_BASE_URL`) + rebuild OpenNext.
2. **HTTP 429 sur tous les scrapings** → cause racine : **empreinte TLS (JA3)**
   bloquée par Cloudflare, pas l'IP. Fix : `curl_cffi` en `impersonate="chrome"` +
   retry intelligent.
3. **Build Cloudflare `npm ci` en échec** → `package-lock.json` désynchronisé
   (`@emnapi/wasi-threads` 1.2.1 vs 1.2.3) ; npm ≥ 11 valide strictement. Fix :
   lock régénéré + champ `allowScripts`.

### Slide 7 — Résultats & chiffres (0:45)
- 6 scopes scrapés, **2 487 produits**, **12 guides**, exportables en 3 formats.
- Correctif 429 vérifié en prod : kleman 228 / andre 1 648 produits.
- CI verte (backend `pytest`, frontend `vitest` + `next build`).

### Slide 8 — Améliorations possibles (0:45)
- Worker de scraping dédié (ARQ/Celery) pour découpler de l'API.
- Pagination complète andre.fr (cap actuel 10 pages), proxies résidentiels.
- Webhooks Shopify / réservation HTTP (ETags) pour du quasi-temps réel.
- Authentification + quotas multi-clients pour un vrai SaaS.

### Slide 9 — Conclusion (0:30)
- Livré : code prêt prod, démo en ligne, tests, CI/CD, docs.
- Prêt à présenter : remercier + ouvrir le Q&A.

**Total ~ 9 min** + Q&A.

---

## 4. Scénario de démo (à exécuter pendant la présentation)

1. Ouvrir le **dashboard** → totaux produits / guides visibles.
2. Aller sur **Nouveau scraping** → saisir
   `https://kleman-france.com/collections/chaussures-accessoires` → lancer.
3. Réponse **202** immédiate → ouvrir le **suivi du job** → statut `running` → `completed`.
   *Prévoir ~45 s à 1 min 30 selon le réseau.*
4. Aller dans **Produits** → résultats kleman visibles (ou filtrer `CONVOI`).
   Cliquer sur une fiche → **variantes** (pointures, prix, dispo, SKU).
5. Ouvrir **Guides de taille** → le guide kleman « Guide des tailles » extrait.
6. Aller dans **Exports** → télécharger le **CSV** et montrer le contenu.
7. Optionnel : Swagger `https://fitler-test.onrender.com/docs` → `GET /health` /
   `GET /products` exécutés en direct.

> ⚠️ Si le scrape live tarde (Cloudflare rate limit), montrer d'abord les données
> déjà en base (2 487 produits), puis lancer le scrape sans insister.

---

## 5. Points techniques à valoriser (si on creuse)

- **Stratégies de scraping en cascade** :
  `shopify_api` (`/products.json`) → `jsonld` (JSON-LD embarqué) → `html`
  (liens produits). Chaque stratégie est une classe indépendante et testable ;
  repli automatique.
- **Guides de taille** : détection par tables HTML, pages dédiées, accordéons,
  popups, hooks JS courants ; jamais bloquant pour le job.
- **`BackgroundTasks`** : réponse `202` immédiate, l'utilisateur n'attend pas les
  appels réseau (remplaçable par un worker sans réécrire l'API).
- **Tri sécurisé** : `sort` contraint par regex pour ne jamais injecter de
  colonne SQL arbitraire.
- **Driver psycopg3 + Neon pooler** : résolution automatique
  `postgresql://` → `postgresql+psycopg://`.

## 6. Difficultés détaillées (réponses à « qu'est-ce qui a été dur ? »)

Voir `FIXES.md` pour le détail complet. Résumé :

| # | Problème | Cause racine | Correctif |
|---|---|---|---|
| 1 | Frontend appelle `localhost:8000` en prod | Variable `NEXT_PUBLIC_*` lue au runtime au lieu du build | URL gravée au build + rebuild OpenNext |
| 2 | HTTP 429 sur tous les scrapings | Empreinte TLS (JA3) d'httpx bloquée par Cloudflare | `curl_cffi` impersonation Chrome + retry tenacity plafonné |
| 3 | Build Cloudflare `npm ci` EUSAGE | `package-lock.json` désync (`@emnapi/wasi-threads`) | Lock régénéré + `allowScripts` dans `package.json` |

## 7. Q&A anticipé

**Pourquoi pas Celery/ARQ ?**
`BackgroundTasks` suffit pour un MVP ; la frontière service permet d'ajouter un
worker dédié sans réécrire l'API.

**Pourquoi SQLite en local et PostgreSQL en prod ?**
SQLite = zéro friction pour démarrer ; PostgreSQL (Neon pooler) en prod pour la
concurrence et le déploiement managé.

**Comment le scraper gère les anti-bots ?**
Impersonation du navigateur (curl_cffi `impersonate="chrome"`), headers
complets, retry avec backoff tenant compte de `Retry-After` (plafonné), User-Agent
navigateur.

**Et si la boutique n'a pas d'API Shopify publique ?**
Les stratégies `jsonld` puis `html` prennent le relais (andre.fr a été scrapé
entièrement en HTML/JSON-LD).

**Comment éviter les doublons ?**
Upsert par `handle` Shopify → idempotent.

**Et si une boutique change de structure ?**
Les stratégies sont cloisonnées : on ajoute/corrige une stratégie sans toucher au
reste. Les échecs de guides ne font jamais échouer le job.

## 8. Captures d'écran

Dossier [`docs/presentation/`](docs/presentation/) :
`01-dashboard`, `02-scrape`, `03-products`, `04-product-detail`,
`05-size-guides`, `06-exports`, `07-api-docs`.
