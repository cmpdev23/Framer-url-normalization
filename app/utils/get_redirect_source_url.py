#utils/get_redirect_source_url.py
from utils.cloudflare_api import CloudflareAPI
from urllib.parse import urlparse
import logging

# Configuration des logs pour ce module
logger = logging.getLogger(__name__)


def get_redirect_source_url():
    """
    Récupère toutes les URLs source (source_url) des listes de redirection de Cloudflare.
    Les URLs sont normalisées pour ne conserver que le chemin avec un slash final.

    Retourne :
        list : Une liste unique contenant tous les chemins d'URL normalisés.
    """
    cloudflare_api = CloudflareAPI()
    all_source_urls = []

    try:
        # Récupérer toutes les listes de redirection
        lists = cloudflare_api.get_lists()

        for redirect_list in lists:
            list_name = redirect_list['name']
            list_id = redirect_list['id']
            logger.info(f"Traitement de la liste : {list_name} (ID: {list_id})")

            # Récupérer les éléments de la liste
            list_items = cloudflare_api.get_list_items(list_id)
            logger.info(f"Nombre total de redirections récupérées : {len(list_items)}")

            # Extraire et normaliser les URLs source
            for item in list_items:
                if 'redirect' in item and 'source_url' in item['redirect']:
                    source_url = item['redirect']['source_url']
                    # Parser l'URL pour extraire uniquement le chemin
                    parsed_url = urlparse(source_url)
                    pathname = parsed_url.path
                    # Ajouter un slash final si nécessaire
                    if not pathname.endswith('/'):
                        pathname += '/'
                    all_source_urls.append(pathname)

        logger.info("Toutes les URLs sources ont été récupérées et normalisées.")
        return all_source_urls

    except Exception as e:
        logger.error(f"Une erreur est survenue lors de la récupération des URLs sources : {e}")
        return []
