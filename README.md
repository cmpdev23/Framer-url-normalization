# URL Slash Redirect System
> Solution de gestion des URLs pour la migration WordPress vers Framer

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Framer](https://img.shields.io/badge/Framer-Migration-blue.svg)](https://www.framer.com/)
[![WordPress](https://img.shields.io/badge/WordPress-Migration-lightgrey.svg)](https://wordpress.org/)

## 📋 Table des Matières
- [Contexte détaillé](#contexte-détaillé)
- [Problématique WordPress → Framer](#problématique)
- [Solution technique](#solution-technique)
  - [Architecture Cloudflare](#architecture-cloudflare)
  - [Script de synchronisation](#script-de-synchronisation)
- [Installation et configuration](#installation-et-configuration)
- [Utilisation](#utilisation)
- [Automatisation](#automatisation)
- [Contribution](#contribution)

## 🎯 Contexte Détaillé

### Le Défi de la Migration vers Framer
Lors de la migration d'un site WordPress vers Framer, un défi majeur se présente : la gestion des URLs. Ce projet résout spécifiquement ce problème peu documenté mais critique pour le SEO.

### Situation WordPress
Dans WordPress, la gestion des URLs était simplifiée :
- Toutes les URLs étaient indexées avec un slash final (/)
- Le fichier `.htaccess` gérait automatiquement les redirections
- Configuration type WordPress :
  ```apache
  <IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
  RewriteBase /
  RewriteRule ^index\.php$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.php [L]
  </IfModule>
  ```

### Particularité de Framer
Framer traite les URLs différemment :
- Une URL avec slash final est considérée différente de la même URL sans slash
- Exemple : `/assurance-vie/` ≠ `/assurance-vie`
- Pas de système de redirection automatique intégré
- Impact potentiel sur le SEO existant

## 🔍 Problématique

### Avant (WordPress)
```plaintext
exemple.com/page/   ✅ Accessible directement
exemple.com/page    ✅ Redirigé automatiquement vers /page/
```

### Après (Framer sans solution)
```plaintext
exemple.com/page/   ✅ Accessible si configuré avec slash
exemple.com/page    ❌ Erreur 404 même si /page/ existe
```

### Impact SEO
- Perte potentielle du référencement existant
- Fragmentation des métriques SEO
- Expérience utilisateur dégradée

## 💡 Solution Technique

### Architecture Cloudflare

#### 1. Worker Cloudflare
Le Worker agit comme un middleware intelligent :
```js
// Extrait du Worker
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  // Logique de redirection intelligente
  if (validUrls.includes(pathWithSlash)) {
    // Redirection 301 si nécessaire
  }
}
```

#### 2. KV Store
Base de données clé-valeur pour :
- Stockage des URLs valides
- Métadonnées de synchronisation
- Cache performant

### Script de Synchronisation

#### Composants
```plaintext
./
├── .env                        # Configuration
├── app.py                      # API Flask
└── utils/
    ├── cloudflare_api.py       # Interface Cloudflare
    ├── config.py               # Gestion config
    └── get_redirect_source_url.py
```

#### Fonctionnalités
1. Récupération des URLs :
   - Parse le sitemap Framer
   - Collecte les redirections existantes
   - Normalise les formats

2. Synchronisation intelligente :
   - Compare les hashes pour détecter les changements
   - Met à jour le KV Store si nécessaire
   - Maintient les métadonnées à jour

## ⚙️ Installation et Configuration

### Variables d'Environnement
```env
CLOUDFLARE_ACCOUNT_ID=votre_id
CLOUDFLARE_NAMESPACE_ID=votre_namespace
CLOUDFLARE_API_TOKEN=votre_token
CLOUDFLARE_EMAIL=votre_email
GLOBAL_API_TOKEN=votre_token_global
SITEMAP_URL=https://votre-site.com/sitemap.xml
```

### Dépendances
```bash
# Python 3.8+ recommandé
pip install -r requirements.txt
```

## 📝 Utilisation

### API Flask
```bash
# Lancement
python app.py

# Endpoints
POST /sync-urls    # Lance la synchronisation
GET /get-metadata  # État actuel
```

### Surveillance
```json
{
    "success": true,
    "metadata": {
        "last_update": "2024-12-19T10:00:00",
        "urls_count": 150,
        "urls_hash": "abc123..."
    }
}
```

## 🤖 Automatisation

### Cron Job Recommandé
```bash
# Synchronisation quotidienne
0 0 * * * /usr/bin/curl -X POST http://localhost:5000/sync-urls
```

## 🤝 Contribution

Les contributions sont bienvenues ! Particulièrement :
- Améliorations de la détection des URLs
- Optimisations de performance
- Documentation de cas d'usage Framer spécifiques

1. Fork le projet
2. Créez une branche (`feature/amelioration`)
3. Testez minutieusement
4. Proposez une Pull Request

## 📚 Ressources Additionnelles
- [Documentation Framer](https://www.framer.com/docs/)
- [API Cloudflare Workers](https://developers.cloudflare.com/workers/)
- [Gestion SEO lors des migrations](https://developers.google.com/search/docs/advanced/crawling/site-migrations)