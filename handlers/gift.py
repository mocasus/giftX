"""Gift command handler — full flow: parse target → pilih durasi → execute."""

import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import BOT_TOKEN, DURATIONS

logger = logging.getLogger(__name__)

# --- /gift @username ---
async def cmd_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parse /gift <username> → show duration picker."""
    args = context.args

    if not args:
        await update.message.reply_text(
            "❌ *Usage:* `/gift @username`\n\n"
            "Contoh: `/gift @elonmusk`",
            parse_mode="Markdown",
        )
        return

    target = args[0].lstrip("@").strip()
    context.user_data["gift_target"] = target

    # Pilih durasi
    keyboard = []
    for key, label in DURATIONS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"🎁 {label}",
                callback_data=f"gift:duration:{key}:{target}",
            )
        ])
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="gift:cancel")])

    await update.message.reply_text(
        f"🎁 *Gift Premium untuk @{target}*\n\n"
        f"Pilih durasi:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# --- callback: pilih durasi → execute ---
async def cb_gift_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User picked a duration → run gift flow."""
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    if len(data) < 4:
        return

    _, _, duration_key, target = data

    label = DURATIONS.get(duration_key, duration_key)

    await query.edit_message_text(
        f"⏳ *Processing...*\n\n"
        f"Gifting {label} ke @{target}...",
        parse_mode="Markdown",
    )

    try:
        from xploit.gift_flow import run_gift
        user_id = update.effective_user.id
        result = await run_gift(target, user_id, duration_key)

        if result["success"]:
            tgt = target
            if result.get("screenshot"):
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=open(result["screenshot"], "rb"),
                    caption=f"✅ *Success!*\n@{tgt} dapet {label} X Premium 🎁",
                    parse_mode="Markdown",
                )
                # Update processing message too
                await query.edit_message_text(
                    f"✅ *Success!*\n@{tgt} dapet {label} X Premium 🎁\n📸 Screenshot di atas",
                    parse_mode="Markdown",
                )
            else:
                await query.edit_message_text(
                    f"✅ *Success!*\n@{tgt} dapet {label} X Premium 🎁",
                    parse_mode="Markdown",
                )
        else:
            err = result.get("error", "Unknown error")
            await query.edit_message_text(
                f"❌ *Gagal:* {err}\n\nCoba lagi atau cek log.",
                parse_mode="Markdown",
            )
    except Exception as e:
        logger.exception("Gift flow error")
        await query.edit_message_text(
            f"💥 *Error:* {str(e)}",
            parse_mode="Markdown",
        )


# --- callback: cancel ---
async def cb_gift_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🚫 *Dibatalkan.*", parse_mode="Markdown")


def register(app: Application) -> None:
    app.add_handler(CommandHandler("gift", cmd_gift))
    app.add_handler(CallbackQueryHandler(cb_gift_duration, pattern=r"^gift:duration:"))
    app.add_handler(CallbackQueryHandler(cb_gift_cancel, pattern=r"^gift:cancel$"))
