<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/python-3.11%2B-green?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-red?style=flat-square" alt="license">
</p>

# 🎁 giftX

Auto-gift X Premium via SEPA bank transfer exploit — fully automated Telegram bot.

---

## 📌 Cara Kerja

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│  Telegram   │──▶│    giftX     │──▶│  Browser     │
│  /gift @X   │    │   (bot)     │    │  (nodriver) │
└─────────────┘    └──────┬───────┘    └──────┬───────┘
                          │                    │
                    ┌─────▼──────┐    ┌───────▼──────┐
                    │  Proxy DE  │    │  X.com       │
                    │  (Jerman)  │    │  (headless)  │
                    └────────────┘    └──────────────┘
```

**Step by step:**
1. **Login** — Akun A (premium) login ke X via browser headless
2. **Target** — Buka profil Akun B (target)
3. **Gift** — Klik 🎁, pilih durasi (3/6/12 bulan)
4. **Payment** — Pilih Bank Transfer / SEPA
5. **Form** — Isi detail bank Jerman (statis)
6. **Submit** — Invoice muncul, Akun B auto-upgrade dalam 1-5 menit 🗿

> **Kenapa bisa?** X.com tidak memverifikasi real-time apakah rekening bank benar-benar ada. Begitu invoice terbit, akun target langsung dapat akses premium. Charge gagal nanti — tapi premium tetap aktif selama siklus billing saat ini.

---

## ⚠️ Syarat

| Syarat | Detail |
|--------|--------|
| **Akun A** | X Premium (Blue/Verified) aktif |
| **Akun B** | Belum pernah premium |
| **IP** | Jerman bersih (residential proxy recommended) |
| **Akun** | Akun baru (fresh) = success rate tertinggi |

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/mocasus/giftX.git
cd giftX

# Install deps
pip install -r requirements.txt

# Setup env
cp .env.example .env
nano .env  # ⬅️ isi kredensial

# Run
python bot.py
```

### Env Variables

```ini
# Telegram
BOT_TOKEN=123456:ABC-DEF1234gh
ADMIN_IDS=123456789

# X.com Akun A (premium)
X_EMAIL=akunA@gmail.com
X_PASSWORD=password123
X_2FA_SECRET=JBSWY3DPEHPK3PXP    # optional — TOTP secret jika 2FA aktif

# Proxy Jerman
PROXY_URL=http://user:pass@de-proxy.example.com:8080
```

---

## 📋 Commands

| Command | Role | Description |
|---------|------|-------------|
| `/start` | All | Main menu |
| `/gift @username` | All | Gift premium (inline pilih durasi) |
| `/list` | All | Riwayat gift |
| `/cancel` | All | Batalkan proses |
| `/stats` | Admin | Statistik usage |
| `/reload` | Admin | Reload config |

---

## 🗂 Struktur

```
giftX/
├── bot.py              # Entry point
├── config.py           # Konfigurasi + env loader
├── handlers/
│   ├── __init__.py
│   ├── start.py        # /start, /help
│   ├── gift.py         # /gift + callback handler
│   └── list.py         # History
├── xploit/
│   ├── __init__.py
│   ├── browser.py      # Browser + login via nodriver
│   ├── gift_flow.py    # Core gift flow
│   └── proxy.py        # Proxy helper
└── data/               # DB + screenshots
```

---

## 🔧 Troubleshooting

| Error | Penyebab | Fix |
|-------|----------|-----|
| `Tombol gift tidak ditemukan` | Akun A bukan premium | Pakai akun premium |
| `Opsi Bank Transfer tidak muncul` | IP bukan Jerman | Cek proxy/VPN — pastikan IP DE |
| `429 / Rate limited` | Akun di-throttle | Ganti akun, tunggu 15 menit |
| `Login gagal` | Kredensial salah / 2FA | Cek `.env`, generate TOTP jika perlu |
| `Browser crash` | RAM kurang | Minimal 512MB free, close apps lain |

---

## 📸 Screenshots

<p align="center">
  <sub>Flow: /gift → pilih durasi → success</sub>
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
</p>

<p align="center">
  <sub>By mmoaa</sub>
</p>
