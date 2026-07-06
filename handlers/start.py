"""Start command handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
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

async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks from start menu."""
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1] if ":" in query.data else ""

    if action == "gift":
        await query.edit_message_text(
            "🎁 *Gift X Premium*\n\n"
            "Kirim: `/gift @username`\n"
            "Contoh: `/gift @elonmusk`",
            parse_mode="Markdown",
        )
    elif action == "list":
        from db import get_user_orders
        user_id = update.effective_user.id
        orders = get_user_orders(user_id)

        if not orders:
            await query.edit_message_text(
                "📋 *History Gift*\n\n"
                "Belum ada order. Mulai dengan `/gift @username`!",
                parse_mode="Markdown",
            )
        else:
            lines = ["📋 *History Gift*\n"]
            for row in orders:
                oid, uid, target, status, created, completed, err, ss = row
                icon = "✅" if status == "done" else ("❌" if status == "failed" else "⏳")
                lines.append(f"{icon} @{target} — *{status}*")
                lines.append(f"  _{created}_")
            lines.append(f"\nTotal: {len(orders)} order")
            await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
    else:
        await query.edit_message_text("🤷 *Menu gak dikenal.*", parse_mode="Markdown")


def register(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^menu:"))
