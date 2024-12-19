
# utils/cloudflare_api.py


import requests
from .config import Config
import logging

# Configuration des logs pour ce module
logger = logging.getLogger(__name__)


class CloudflareAPI:
    def __init__(self):
        self.account_id = Config.CLOUDFLARE_ACCOUNT_ID
        self.headers = {
            'X-Auth-Email': Config.CLOUDFLARE_EMAIL,
            'X-Auth-Key': Config.GLOBAL_API_TOKEN,
            'Content-Type': 'application/json'
        }

    def get_lists(self):
        """Récupère toutes les listes de redirections"""
        url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/rules/lists'
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            logger.info("Listes de redirections récupérées avec succès")
            return response.json()['result']
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des listes : {e}")
            raise

    def get_list_items(self, list_id):
        """Récupère tous les éléments d'une liste spécifique avec gestion de la pagination"""
        base_url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/rules/lists/{list_id}/items'

        all_items = []
        page = 1
        per_page = 100  # Maximum permis par l'API

        try:
            while True:
                params = {
                    'page': page,
                    'per_page': per_page
                }

                logger.info(f"Récupération de la page {page} pour la liste {list_id}...")
                response = requests.get(base_url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                items = data['result']
                all_items.extend(items)

                # Vérifier s'il y a d'autres pages
                total_count = data.get('result_info', {}).get('total_count', 0)
                total_pages = (total_count + per_page - 1) // per_page

                if page >= total_pages:
                    break

                page += 1

            logger.info(f"Total des redirections récupérées : {len(all_items)}")
            return all_items
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des éléments pour la liste {list_id} : {e}")
            raise
