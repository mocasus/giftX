"""Start command handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import ADMIN_IDS

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id in ADMIN_IDS
    
    text = (
        f"🎁 <b>giftX — Auto Gift X Premium</b>\n\n"
        f"Halo {user.first_name}!\n"
        f"Bot ini auto-gift X Premium ke akun target\n"
        f"pakai exploit bank transfer SEPA.\n\n"
        f"📌 <b>Cara pakai:</b>\n"
        f"<code>/gift @username</code> — Gift premium (3/6/12 bln)\n"
        f"<code>/list</code> — Lihat history gift\n"
    )
    
    if is_admin:
        text += f"\n🔧 <b>Admin:</b>\n<code>/stats</code> — Statistik\n<code>/reload</code> — Reload config\n"
    
    keyboard = [
        [InlineKeyboardButton("🎁 Gift Premium", callback_data="menu:gift")],
        [InlineKeyboardButton("📋 History", callback_data="menu:list")],
    ]
    
    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 <b>giftX Help</b>\n\n"
        "<code>/gift @username</code> — Gift X Premium (pilih durasi)\n"
        "<code>/list</code> — History gift\n"
        "<code>/cancel</code> — Batalkan proses\n",
        parse_mode="HTML",
    )

async def cb_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks from start menu."""
    query = update.callback_query
    await query.answer()

    action = query.data.split(":")[1] if ":" in query.data else ""

    if action == "gift":
        await query.edit_message_text(
            "🎁 <b>Gift X Premium</b>\n\n"
            "Kirim: <code>/gift @username</code>\n"
            "Contoh: <code>/gift @elonmusk</code>",
            parse_mode="HTML",
        )
    elif action == "list":
        from db import get_user_orders
        user_id = update.effective_user.id
        orders = get_user_orders(user_id)

        if not orders:
            await query.edit_message_text(
                "📋 <b>History Gift</b>\n\n"
                "Belum ada order. Mulai dengan <code>/gift @username</code>!",
                parse_mode="HTML",
            )
        else:
            lines = ["📋 <b>History Gift</b>\n"]
            for row in orders:
                oid, uid, target, status, created, completed, err, ss = row
                icon = "✅" if status == "done" else ("❌" if status == "failed" else "⏳")
                lines.append(f"{icon} @{target} — <b>{status}</b>")
                lines.append(f"  <i>{created}</i>")
            lines.append(f"\nTotal: {len(orders)} order")
            await query.edit_message_text("\n".join(lines), parse_mode="HTML")
    else:
        await query.edit_message_text("🤷 <b>Menu gak dikenal.</b>", parse_mode="HTML")


def register(app: Application) -> None:
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(cb_menu, pattern=r"^menu:"))
