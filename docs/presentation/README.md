# Captures d'écran — démo

Capturées depuis la production (`https://fitler-test.ibra-so-sow.workers.dev`).

| Fichier | Page |
|---|---|
| `01-dashboard.png` | Accueil / dashboard (totaux) |
| `02-scrape.png` | Formulaire de nouveau scraping |
| `03-products.png` | Catalogue produits (pagination, recherche) |
| `04-product-detail.png` | Fiche produit : variantes, prix, disponibilité, SKU |
| `05-size-guides.png` | Guides de taille extraits |
| `06-exports.png` | Téléchargements JSON / CSV / XLSX |
| `07-api-docs.png` | Swagger UI de l'API (`/docs`) |

Re-capturer manuellement si nécessaire :

```powershell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" `
  "--headless=new" "--disable-gpu" "--hide-scrollbars" `
  "--window-size=1440,900" "--virtual-time-budget=25000" `
  "--screenshot=docs\presentation\01-dashboard.png" `
  "https://fitler-test.ibra-so-sow.workers.dev/"
```
