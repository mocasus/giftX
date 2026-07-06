"""Gift command — main exploit flow handler with duration selection."""

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from db import add_order, update_order, get_user_orders
from xploit.gift_flow import run_gift
from config import DURATIONS

_running = {}

async def cmd_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gift @username command."""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "❌ *Format salah!*\n"
            "Gunakan: `/gift @username`\n"
            "Contoh: `/gift @elonmusk`",
            parse_mode="Markdown",
        )
        return
    
    if user.id in _running:
        await update.message.reply_text("⏳ Masih ada proses berjalan. Tunggu selesai atau `/cancel`.")
        return
    
    target = context.args[0].lstrip("@").strip()
    
    if len(target) < 2 or len(target) > 30:
        await update.message.reply_text("❌ Username tidak valid!")
        return
    
    # Simpan target di context
    context.user_data["gift_target"] = target
    
    # Tampilkan pilihan durasi
    keyboard = []
    row = []
    for months, label in DURATIONS.items():
        row.append(InlineKeyboardButton(label, callback_data=f"dur:{months}"))
    keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="gift:cancel")])
    
    await update.message.reply_text(
        f"🎁 *Gift X Premium*\n\n"
        f"🎯 Target: @{target}\n\n"
        f"⏰ *Pilih durasi:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle duration selection callback."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    duration = query.data.split(":", 1)[1]
    target = context.user_data.get("gift_target", "")
    
    if not target:
        await query.edit_message_text("❌ Session expired. Ulangi `/gift @username`.")
        return
    
    if user.id in _running:
        await query.edit_message_text("⏳ Masih ada proses berjalan.")
        return
    
    # Create order
    order_id = add_order(user.id, target)
    duration_label = DURATIONS.get(duration, duration)
    
    await query.edit_message_text(
        f"🎁 *Gift X Premium*\n\n"
        f"🎯 Target: @{target}\n"
        f"📋 Order: #{order_id}\n"
        f"⏰ Durasi: {duration_label}\n\n"
        f"🔐 Login ke Akun A...",
        parse_mode="Markdown",
    )
    
    _running[user.id] = True
    
    try:
        await query.edit_message_text(
            f"🎁 *Gift X Premium*\n\n"
            f"🎯 Target: @{target}\n"
            f"📋 Order: #{order_id}\n"
            f"⏰ Durasi: {duration_label}\n"
            f"🌐 Ambil detail bank...",
            parse_mode="Markdown",
        )
        
        result = await run_gift(target, user.id, duration)
        
        if result["success"]:
            update_order(order_id, "done", screenshot=result.get("screenshot"))
            text = (
                f"✅ *Gift berhasil!*\n\n"
                f"🎯 @{target}\n"
                f"📋 Order: #{order_id}\n"
                f"⏰ Durasi: {duration_label}\n"
                f"💰 Bank transfer invoice udah muncul\n\n"
                f"⏰ Cek akun target 1-5 menit lagi — harusnya udah premium!"
            )
        else:
            update_order(order_id, "failed", error=result.get("error"))
            text = (
                f"❌ *Gift gagal*\n\n"
                f"🎯 @{target}\n"
                f"📋 Order: #{order_id}\n"
                f"📝 Error: {result.get('error', 'Unknown')}\n\n"
                f"Coba lagi atau cek log."
            )
        
        await query.edit_message_text(text, parse_mode="Markdown")
        
        if result.get("screenshot"):
            try:
                with open(result["screenshot"], "rb") as f:
                    await update.effective_chat.send_photo(f)
            except Exception:
                pass
        
    except Exception as e:
        update_order(order_id, "failed", error=str(e))
        await query.edit_message_text(
            f"❌ *Error fatal*\n\nOrder #{order_id}\n`{str(e)[:200]}`",
            parse_mode="Markdown",
        )
    finally:
        _running.pop(user.id, None)
        context.user_data.pop("gift_target", None)

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel gift operation."""
    query = update.callback_query
    await query.answer("Dibatalkan")
    context.user_data.pop("gift_target", None)
    await query.edit_message_text("❌ Gift dibatalkan.")

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    orders = get_user_orders(user.id)
    
    if not orders:
        await update.message.reply_text("📭 Belum ada history gift.")
        return
    
    lines = ["📋 *History Gift Kamu:*\n"]
    for o in orders[:10]:
        icon = {"done": "✅", "failed": "❌", "pending": "⏳"}.get(o[3], "❓")
        lines.append(f"{icon} #{o[0]} — @{o[2]} — {o[3]}")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in _running:
        _running.pop(user.id, None)
        await update.message.reply_text("🛑 Operasi dibatalkan.")
    else:
        await update.message.reply_text("Tidak ada proses yang berjalan.")

def register(app: Application) -> None:
    app.add_handler(CommandHandler("gift", cmd_gift))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CallbackQueryHandler(duration_callback, pattern="^dur:"))
    app.add_handler(CallbackQueryHandler(cancel_callback, pattern="^gift:cancel$"))
