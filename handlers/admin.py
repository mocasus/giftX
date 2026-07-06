"""Admin-only handlers."""

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import ADMIN_IDS
from db import get_stats, init_db

def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    
    total, done, failed = get_stats()
    await update.message.reply_text(
        f"📊 *giftX Stats*\n\n"
        f"Total orders: {total}\n"
        f"✅ Sukses: {done}\n"
        f"❌ Gagal: {failed}\n"
        f"📈 Success rate: {(done/total*100):.1f}%" if total > 0 else "📈 N/A",
        parse_mode="Markdown",
    )

async def cmd_reload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not _is_admin(user.id):
        await update.message.reply_text("⛔ Admin only.")
        return
    
    import importlib
    import config
    importlib.reload(config)
    await update.message.reply_text("🔄 Config reloaded!")

def register(app: Application) -> None:
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("reload", cmd_reload))
