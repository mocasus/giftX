# 🎁 giftX

Auto-gift X Premium via SEPA bank transfer exploit — Telegram bot.

## Flow (Simpel)

```
1. Akun A (Premium) login
2. Buka profil Akun B (target)
3. Klik 🎁 → pilih durasi (3/6/12 bulan)
4. Di halaman pembayaran, pilih Bank Transfer (SEPA)
5. Isi detail bank Jerman (statis, gak perlu SMS service)
6. Submit → invoice muncul
7. Akun B auto-upgrade dalam 1-5 menit 🗿
```

**Syarat:**
- Akun A: X Premium aktif
- Akun B: belum pernah premium
- IP Jerman bersih (proxy/VPN)
- Akun baru work best

## Setup

```bash
git clone https://github.com/mocasus/giftX
cd giftX
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan kredensial kamu
python bot.py
```

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/gift @username` | Gift premium (pilih durasi di inline keyboard) |
| `/list` | View gift history |
| `/cancel` | Batalin proses |
| `/stats` | Admin: statistik |
| `/reload` | Admin: reload config |

## Env

| Var | Required | Notes |
|-----|----------|-------|
| `BOT_TOKEN` | ✅ | From @BotFather |
| `X_EMAIL` | ✅ | Akun A premium |
| `X_PASSWORD` | ✅ | Akun A password |
| `X_2FA_SECRET` | ❌ | TOTP secret if 2FA on |
| `PROXY_URL` | ✅ | German proxy |

## License

By mmoaa
