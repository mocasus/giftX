"""Start command handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from config import ADMIN_IDS

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id in ADMIN_IDS
    
    text = (
        f"🎁 *giftX — Auto Gift X Premium*\n\n"
        f"Halo {user.first_name}!\n"
        f"Bot ini auto-gift X Premium ke akun target\n"
        f"pakai exploit bank transfer SEPA.\n\n"
        f"📌 *Cara pakai:*\n"
        f"`/gift @username` — Gift premium (3/6/12 bln)\n"
        f"`/list` — Lihat history gift\n"
    )
    
    if is_admin:
        text += f"\n🔧 *Admin:*\n`/stats` — Statistik\n`/reload` — Reload config\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Gift Premium", callback_data="menu:gift")],
        [InlineKeyboardButton("📋 History", callback_data="menu:list")],
    ]
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 *giftX Help*\n\n"
        "`/gift @username` — Gift X Premium (pilih durasi)\n"
        "`/list` — History gift\n"
        "`/cancel` — Batalkan proses\n",
        parse_mode="Markdown",
    )

def register(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
