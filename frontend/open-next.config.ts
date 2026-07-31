// Configuration du déploiement Cloudflare (OpenNext).
// L'application étant statique (aucun cache serveur nécessaire),
// on conserve la configuration par défaut sans cache R2.
import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({});
