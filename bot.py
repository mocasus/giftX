#!/usr/bin/env python3
"""giftX — Telegram bot for automated X Premium gifting."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env before anything
load_dotenv(Path(__file__).parent / ".env")

from telegram.ext import Application
from config import BOT_TOKEN, READY
from db import init_db

async def _post_init(app: Application):
    """Called after bot starts."""
    me = await app.bot.get_me()
    print(f"🤖 @{me.username} online!")
    init_db()
    print("📦 Database siap!")

def main():
    if not READY:
        print("❌ Config tidak lengkap! Isi .env dulu.")
        print("   BOT_TOKEN + X_EMAIL + X_PASSWORD wajib diisi.")
        sys.exit(1)
    
    app = Application.builder().token(BOT_TOKEN).post_init(_post_init).build()
    
    # Register all handlers
    from handlers import start, gift, admin
    start.register(app)
    gift.register(app)
    admin.register(app)
    
    print("🚀 giftX bot starting...")
    app.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
