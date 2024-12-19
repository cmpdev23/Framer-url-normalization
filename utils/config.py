# utils/config.py

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL')
    GLOBAL_API_TOKEN = os.getenv('GLOBAL_API_TOKEN')

    @classmethod
    def validate(cls):
        required_vars = [
            'CLOUDFLARE_ACCOUNT_ID',
            'CLOUDFLARE_EMAIL',
            'GLOBAL_API_TOKEN',
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing)}")