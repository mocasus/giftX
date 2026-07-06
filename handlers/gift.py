"""Gift command — main exploit flow handler."""

import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from db import add_order, update_order, get_user_orders
from xploit.gift_flow import run_gift

# Track running tasks per user
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
    
    # Basic validation
    if len(target) < 2 or len(target) > 30:
        await update.message.reply_text("❌ Username tidak valid!")
        return
    
    # Create order
    order_id = add_order(user.id, target)
    
    msg = await update.message.reply_text(
        f"🎁 *Memulai gift X Premium*\n\n"
        f"🎯 Target: @{target}\n"
        f"📋 Order ID: #{order_id}\n\n"
        f"⏳ Membuka browser...",
        parse_mode="Markdown",
    )
    
    _running[user.id] = True
    
    try:
        await msg.edit_text(
            f"🎁 *Gift X Premium*\n\n"
            f"🎯 Target: @{target}\n"
            f"📋 Order: #{order_id}\n"
            f"🔐 Login ke Akun A...",
            parse_mode="Markdown",
        )
        
        result = await run_gift(target, user.id)
        
        if result["success"]:
            update_order(order_id, "done", screenshot=result.get("screenshot"))
            text = (
                f"✅ *Gift berhasil!*\n\n"
                f"🎯 @{target}\n"
                f"📋 Order: #{order_id}\n"
                f"💰 Bank transfer invoice udah muncul — tinggal tunggu upgrade\n\n"
                f"⏰ Biasanya 1-5 menit akun B bakal premium."
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
        
        await msg.edit_text(text, parse_mode="Markdown")
        
        # Send screenshot if available
        if result.get("screenshot"):
            try:
                with open(result["screenshot"], "rb") as f:
                    await update.message.reply_photo(f)
            except Exception:
                pass
        
    except Exception as e:
        update_order(order_id, "failed", error=str(e))
        await msg.edit_text(
            f"❌ *Error fatal*\n\nOrder #{order_id}\n`{str(e)[:200]}`",
            parse_mode="Markdown",
        )
    finally:
        _running.pop(user.id, None)

async def cmd_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's gift history."""
    user = update.effective_user
    orders = get_user_orders(user.id)
    
    if not orders:
        await update.message.reply_text("📭 Belum ada history gift.")
        return
    
    lines = ["📋 *History Gift Kamu:*\n"]
    for o in orders[:10]:
        status_icon = {"done": "✅", "failed": "❌", "pending": "⏳"}.get(o[3], "❓")
        lines.append(f"{status_icon} #{o[0]} — @{o[2]} — {o[3]}")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel running operation."""
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
