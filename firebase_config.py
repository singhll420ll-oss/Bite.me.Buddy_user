"""
Firebase Configuration (NO ADMIN SDK)
Only config values
"""

import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:

    WEB_CONFIG = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    }

    SERVICE_ACCOUNT_PATH = os.getenv(
        "SERVICE_ACCOUNT_PATH",
        "bite-me-buddy-service-account-key.json"
    )