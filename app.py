# app.py
import logging
from flask import Flask, jsonify
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import os
from dotenv import load_dotenv
import hashlib
import json
from utils.get_redirect_source_url import get_redirect_source_url  # Importer la fonction

load_dotenv()

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,  # Niveau par défaut
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Affiche les logs dans la console
        logging.FileHandler("app.log")  # Sauvegarde les logs dans un fichier
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


class CloudflareKVSync:
    def __init__(self):
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.namespace_id = os.getenv('CLOUDFLARE_NAMESPACE_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        self.sitemap_url = os.getenv('SITEMAP_URL')

        if not all([self.account_id, self.namespace_id, self.api_token, self.sitemap_url]):
            logger.error("Toutes les variables d'environnement sont requises")
            raise ValueError("Toutes les variables d'environnement sont requises")

        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def get_current_metadata(self):
        """Récupère les métadonnées actuelles du KV"""
        try:
            api_url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/storage/kv/namespaces/{self.namespace_id}/values/metadata'
            response = requests.get(api_url, headers=self.headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            logger.info("Métadonnées récupérées avec succès")
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des métadonnées: {str(e)}")
            return None

    def fetch_sitemap(self):
        """Récupère et parse le sitemap XML"""
        try:
            response = requests.get(self.sitemap_url)
            response.raise_for_status()
            # Parser le XML
            root = ET.fromstring(response.content)
            urls = []
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                parsed_url = requests.utils.urlparse(url.text)
                pathname = parsed_url.path
                if not pathname.endswith('/'):
                    pathname += '/'
                urls.append(pathname)
            # Calculer un hash des URLs pour détecter les changements
            urls_hash = hashlib.md5(json.dumps(sorted(urls)).encode()).hexdigest()
            logger.info("Sitemap récupéré et analysé avec succès")
            return urls, urls_hash
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération du sitemap: {str(e)}")
            raise
        except ET.ParseError as e:
            logger.error(f"Erreur lors du parsing du XML: {str(e)}")
            raise

    def update_kv_store(self, urls, urls_hash):
        """Met à jour le KV store avec les URLs et les métadonnées"""
        metadata = {
            'last_update': datetime.now().isoformat(),
            'urls_count': len(urls),
            'urls_hash': urls_hash,
            'sitemap_url': self.sitemap_url
        }
        try:
            urls_api_url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/storage/kv/namespaces/{self.namespace_id}/values/urls'
            requests.put(urls_api_url, headers=self.headers, json=urls).raise_for_status()

            metadata_api_url = f'https://api.cloudflare.com/client/v4/accounts/{self.account_id}/storage/kv/namespaces/{self.namespace_id}/values/metadata'
            requests.put(metadata_api_url, headers=self.headers, json=metadata).raise_for_status()

            logger.info("KV store mis à jour avec succès")
            return metadata
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la mise à jour du KV store: {str(e)}")
            raise


@app.route('/sync-urls', methods=['POST'])
def sync_urls():
    try:
        syncer = CloudflareKVSync()
        current_metadata = syncer.get_current_metadata()

        sitemap_urls, sitemap_hash = syncer.fetch_sitemap()
        redirect_source_urls = get_redirect_source_url()
        all_urls = list(set(sitemap_urls + redirect_source_urls))
        combined_hash = hashlib.md5(json.dumps(sorted(all_urls)).encode()).hexdigest()

        if current_metadata and current_metadata.get('urls_hash') == combined_hash:
            logger.info("Les URLs sont déjà à jour")
            return jsonify({
                'success': True,
                'status': 'unchanged',
                'metadata': current_metadata,
                'message': 'Les URLs sont déjà à jour'
            }), 200

        new_metadata = syncer.update_kv_store(all_urls, combined_hash)
        logger.info("Mise à jour réussie des URLs")
        return jsonify({
            'success': True,
            'status': 'updated',
            'previous_metadata': current_metadata,
            'new_metadata': new_metadata,
            'changes': {
                'urls_added': len(all_urls) - (current_metadata.get('urls_count', 0) if current_metadata else 0)
            }
        }), 200

    except Exception as e:
        logger.error(f"Erreur lors de la synchronisation des URLs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/get-metadata', methods=['GET'])
def get_metadata():
    """Endpoint pour vérifier l'état actuel des données"""
    try:
        syncer = CloudflareKVSync()
        metadata = syncer.get_current_metadata()

        if metadata:
            logger.info("Métadonnées récupérées avec succès")
            return jsonify({
                'success': True,
                'metadata': metadata
            }), 200
        else:
            logger.warning("Aucune métadonnée trouvée")
            return jsonify({
                'success': False,
                'message': 'Aucune métadonnée trouvée'
            }), 404
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des métadonnées: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Démarrage de l'application Flask")
    app.run(debug=True)
