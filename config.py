"""giftX configuration — loads .env, exposes typed constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

X_EMAIL = os.getenv("X_EMAIL", "")
X_PASSWORD = os.getenv("X_PASSWORD", "")
X_2FA_SECRET = os.getenv("X_2FA_SECRET", "")

PROXY_URL = os.getenv("PROXY_URL", "")

# SMS receive service for bank details
SMS_SERVICE_API_KEY = os.getenv("SMS_SERVICE_API_KEY", "")
SMS_SERVICE_BASE = os.getenv("SMS_SERVICE_BASE", "https://api.sms-activate.org/stubs/handler_api.php")

DB_PATH = os.getenv("DB_PATH", "data/giftx.db")

# Gift duration options (months)
DURATIONS = {
    "3": "3 Months",
    "6": "6 Months", 
    "12": "12 Months",
}

# Validate critical config
READY = bool(BOT_TOKEN and X_EMAIL and X_PASSWORD)
