# 🎁 giftX

Auto-gift X Premium via bank transfer exploit — Telegram bot.

## How It Works

X has a bug in their gift premium flow: when paying via SEPA bank transfer (German region), the system generates an invoice and immediately upgrades the target account — **before verifying payment**. Bank transfers take 1-3 days to clear, so the exploit window is permanent.

```
Akun A (Premium)  →  gift  →  Akun B (Target)
                     ↑
              Bank Transfer (Jerman)
              Invoice muncul → Auto upgrade 🗿
```

## Setup

```bash
git clone https://github.com/mocasus/giftX
cd giftX
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python bot.py
```

## Requirements

- Akun A: X Premium account (active)
- Akun B: Target account username
- German VPN/proxy
- Python 3.11+
- Chrome/Chromium (for nodriver)

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Main menu |
| `/gift @username` | Gift premium to target |
| `/list` | View gift history |
| `/cancel` | Cancel running operation |

## License

By mmoaa
