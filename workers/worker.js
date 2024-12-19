let cachedUrls = null; // Variable de cache
let lastFetchTime = 0; // Timestamp de la dernière récupération

async function getValidUrls() {
  const CACHE_TTL = 86400000; // 24 heures en millisecondes (86 400 000 ms)
  const now = Date.now();

  if (!cachedUrls || now - lastFetchTime > CACHE_TTL) {
    // Si le cache est vide ou expiré, récupérer les données depuis KV
    cachedUrls = await VALID_URLS.get('urls', 'json');
    lastFetchTime = now;
    console.log('URLs récupérées depuis le KV Store');
  } else {
    console.log('Utilisation du cache local des URLs');
  }

  return cachedUrls;
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Configuration
  const STATIC_EXTENSIONS = /\.(ico|png|jpg|jpeg|gif|css|js|svg|woff|woff2|ttf|eot)$/;
  const SPECIAL_PATHS = new Set(['/robots.txt', '/sitemap.xml']);

  // Ne pas traiter les fichiers statiques et pages spéciales
  if (SPECIAL_PATHS.has(path) || STATIC_EXTENSIONS.test(path)) {
    return fetch(request);
  }

  try {
    // Récupérer les URLs valides avec mise en cache
    const validUrls = await getValidUrls();

    if (!validUrls) {
      console.error('Aucune URL valide trouvée dans le KV store');
      return fetch(request);
    }

    // Vérifier si c'est une URL valide (avec ou sans slash)
    const pathWithSlash = path.endsWith('/') ? path : path + '/';
    const pathWithoutSlash = path.endsWith('/') ? path.slice(0, -1) : path;

    if (validUrls.includes(pathWithSlash)) {
      if (!path.endsWith('/')) {
        const redirectUrl = new URL(pathWithSlash, url.origin);
        return Response.redirect(redirectUrl.toString(), 301);
      }
      return fetch(request);
    } else {
      if (path.endsWith('/')) {
        const redirectUrl = new URL(pathWithoutSlash, url.origin);
        return Response.redirect(redirectUrl.toString(), 301);
      }
      return fetch(request);
    }

  } catch (error) {
    console.error('Erreur lors de l\'accès au KV:', error);
    return fetch(request);
  }
}
