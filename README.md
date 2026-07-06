# 🎁 giftX

Auto-gift X Premium via SEPA bank transfer exploit — Telegram bot.

## Flow

```
1. Akun A (Premium) login
2. Buka profil Akun B (target)
3. Klik 🎁 Gift → pilih durasi (3/6/12 bulan)
4. SEBELUM VPN: ambil detail bank dari SMS service
5. Hubungkan VPN Jerman 🇩🇪 → refresh halaman pembayaran
6. Pilih Bank Transfer (SEPA)
7. Isi detail bank
8. Submit → invoice muncul
9. Akun B auto-upgrade dalam 1-5 menit 🗿
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
| `/cancel` | Batalin proses yg lagi jalan |
| `/stats` | Admin: statistik |
| `/reload` | Admin: reload config |

## Env Vars

| Var | Required | Notes |
|-----|----------|-------|
| `BOT_TOKEN` | ✅ | From @BotFather |
| `X_EMAIL` | ✅ | Akun A premium |
| `X_PASSWORD` | ✅ | Akun A password |
| `X_2FA_SECRET` | ❌ | TOTP secret (kalau 2FA on) |
| `PROXY_URL` | ✅ | German proxy (http://user:pass@host:port) |
| `SMS_SERVICE_API_KEY` | ❌ | SMS receive service API (untuk detail bank) |
| `ADMIN_IDS` | ❌ | Comma-separated Telegram user IDs |

## License

By mmoaa
