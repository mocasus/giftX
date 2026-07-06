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

DB_PATH = os.getenv("DB_PATH", "data/giftx.db")

# Validate critical config
READY = bool(BOT_TOKEN and X_EMAIL and X_PASSWORD)
