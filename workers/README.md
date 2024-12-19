# URL Slash Redirect Worker

Un Worker Cloudflare qui gère intelligemment les redirections d'URLs avec ou sans slash final, particulièrement utile lors d'une migration de WordPress vers Framer.

## 🎯 Objectif

Ce Worker résout le problème courant de gestion des URLs lors d'une migration de site, en particulier :
- Maintien de la cohérence des URLs avec/sans slash final
- Préservation du SEO existant
- Gestion automatique des redirections 301
- Compatibilité entre différentes plateformes (WordPress → Framer)

## 🚀 Installation

1. Créez un nouveau Worker dans votre compte Cloudflare
2. Copiez le code du fichier `worker.js`
3. Créez un KV Namespace nommé `VALID_URLS`
4. Liez le KV Namespace à votre Worker

```js
// Exemple de configuration dans le dashboard Cloudflare
// Workers & Pages → votre-worker → Settings → Variables
// Ajoutez une variable KV Namespace binding:
// Variable name: VALID_URLS
// KV Namespace: votre-namespace
```

## 📋 Configuration

Le Worker nécessite une liste d'URLs valides stockée dans le KV Store. Format attendu :

```json
[
  "/",
  "/page-exemple/",
  "/blog/article-exemple/"
]
```

## ⚙️ Fonctionnement

1. **Gestion du Cache**
   - Cache en mémoire des URLs valides
   - TTL de 24 heures
   - Mise à jour automatique à expiration

2. **Traitement des Requêtes**
   - Ignore les fichiers statiques (.jpg, .css, etc.)
   - Ignore les chemins spéciaux (robots.txt, sitemap.xml)
   - Vérifie la présence de l'URL dans la liste valide
   - Redirige vers la version appropriée (avec/sans slash)

3. **Types de Redirections**
   ```
   /page → /page/         (301 redirect)
   /page/ → pas de redirection
   ```

## 🔧 Personnalisation

Modifiez les constantes suivantes selon vos besoins :

```js
const CACHE_TTL = 86400000; // 24 heures en ms
const STATIC_EXTENSIONS = /\.(ico|png|jpg|jpeg|gif|css|js|svg|woff|woff2|ttf|eot)$/;
const SPECIAL_PATHS = new Set(['/robots.txt', '/sitemap.xml']);
```

## 📝 Exemples

1. **URL sans slash**
   ```
   Request: example.com/page
   Response: 301 redirect to example.com/page/
   ```

2. **URL avec slash**
   ```
   Request: example.com/page/
   Response: Direct fetch (no redirect)
   ```

3. **Fichier statique**
   ```
   Request: example.com/image.jpg
   Response: Direct fetch (no redirect)
   ```

## ⚠️ Limitations

- Le cache est lié à l'instance du Worker
- Limite de taille du KV Store selon votre plan Cloudflare
- Les URLs doivent être mises à jour manuellement dans le KV Store

## 🔍 Debugging

Le Worker inclut des logs pour le debugging :
```js
console.log('URLs récupérées depuis le KV Store');
console.log('Utilisation du cache local des URLs');
console.error('Aucune URL valide trouvée dans le KV store');
```

## 📈 Performance

- Cache en mémoire pour réduire les accès au KV Store
- Traitement minimal pour les fichiers statiques
- Redirections 301 pour optimisation SEO

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amélioration`)
3. Commit vos changements (`git commit -m 'Ajout de fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amélioration`)
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.