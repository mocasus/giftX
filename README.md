<p align="center">
  <img src="assets/logo.png" width="120" alt="giftX">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/python-3.11%2B-green?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/license-MIT-red?style=flat-square" alt="license">
</p>

# 🎁 giftX

**Auto-gift X Premium via SEPA bank transfer exploit** — fully automated Telegram bot. Kirim `/gift @username`, bot handle sisanya: login, navigasi, isi form, submit. Target dapet blue check dalam hitungan menit.

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

### Flow detail

| Step | Action | Kenapa |
|------|--------|--------|
| 1 | **Login Akun A** | Pakai browser headless (nodriver) — lebih stealth dari Playwright/Selenium, bypass basic bot detection |
| 2 | **Buka profil Akun B** | X hanya tampilkan tombol 🎁 kalau Akun A premium & Akun B eligible |
| 3 | **Klik gift + pilih durasi** | 3/6/12 bulan — durasi menentukan nominal invoice |
| 4 | **Pilih Bank Transfer / SEPA** | Opsi ini HANYA muncul jika IP terdeteksi dari Jerman 🇩🇪 |
| 5 | **Isi form bank** | IBAN, BIC, nama, alamat — pakai data Jerman statis |
| 6 | **Submit** | Invoice terbit, X langsung kasih premium — **tanpa nunggu pembayaran sukses** |

---

## 🔬 Kenapa Bisa?

Ini bukan "hack" dalam arti tradisional — ini business logic loophole di sistem billing X.com:

```
BILLING FLOW X.COM:

User klik Gift ▸ Pilih SEPA ▸ Isi form bank ▸ Submit
                                          │
                                    ┌─────▼──────┐
                                    │  Invoice   │──▶ Akun B langsung premium ✅
                                    │  terbit    │
                                    └─────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │  X kirim   │──▶ Bank proses 3-5 hari kerja
                                    │  SEPA req  │
                                    └─────┬──────┘
                                          │
                              ┌───────────▼───────────┐
                              │  Rekening gak ada /   │
                              │  dana kurang           │
                              │  → Charge FAILED ❌    │──▶ Premium TETAP aktif
                              └───────────────────────┘     (sampai akhir siklus)
```

**Kunci exploit:** X memberikan akses premium segera setelah invoice terbit (optimistic provisioning), bukan setelah pembayaran confirmed. SEPA transfer butuh 3-5 hari kerja untuk settle — dalam waktu itu, premium sudah dinikmati.

> ⚠️ **Catch:** Akun A yang melakukan gift akan kena tagihan di siklus berikutnya. Pastikan Akun A adalah akun burner/sekali pakai.

---

## 🧬 Tech Stack

| Layer | Tech | Alasan |
|-------|------|--------|
| **Orchestrator** | `python-telegram-bot` v22+ | Async, job queue, mature |
| **Browser** | `nodriver` | Lebih stealth dari Playwright — tidak inject CDP flags, gak terdeteksi sebagai automation |
| **Auth** | `pyotp` | Generate TOTP jika Akun A pakai 2FA |
| **Proxy** | HTTP/SOCKS5 | Harus IP Jerman — X gate SEPA option by geo-IP |
| **DB** | SQLite | Ringan, zero-config, cukup untuk history gift |
| **Runtime** | Python 3.11+ | `asyncio` native, kompatibel dengan semua dep |

### Kenapa `nodriver` bukan Playwright/Selenium?

```
Playwright  → inject `navigator.webdriver = true` (terdeteksi)
Selenium    → tons of side-effects, CDP flags terlihat
nodriver    → pure CDP, no automation markers, bypass basic bot detection
```

X.com tidak se-agresif Cloudflare — mereka gak fingerprint JS secara deep. `nodriver` cukup untuk stealth di sini.

---

## ⚠️ Syarat

| Syarat | Detail | Kenapa |
|--------|--------|--------|
| **Akun A** | X Premium aktif | Butuh akses gift button |
| **Akun B** | Belum pernah premium (atau expired) | Returning user = button gak muncul |
| **IP Jerman** 🇩🇪 | Residential proxy preferred | SEPA option hanya muncul dari IP Jerman |
| **IP bersih** | Bukan DC/datacenter, bukan flagged | X rate-limit IP yang可疑 |
| **Akun fresh** | Umur < 1 minggu ideal | Akun lama lebih mungkin di-flag, rate-limit, atau kena challenge |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/mocasus/giftX.git
cd giftX

# 2. Install
pip install -r requirements.txt

# 3. Setup
cp .env.example .env
nano .env

# 4. Run
python bot.py
```

### `.env` lengkap

```ini
# ─── Telegram ──────────────────────
BOT_TOKEN=123456:ABC-DEF1234gh      # dari @BotFather
ADMIN_IDS=123456789                 # ID Telegram kamu (comma-separated)

# ─── X.com Akun A ─────────────────
X_EMAIL=akunA@gmail.com
X_PASSWORD=password123
X_2FA_SECRET=JBSWY3DPEHPK3PXP      # optional — hanya jika 2FA aktif

# ─── Proxy Jerman ─────────────────
PROXY_URL=http://user:pass@de-proxy.example.com:8080
# atau SOCKS5:
# PROXY_URL=socks5://user:pass@de-proxy.example.com:1080
```

### Dapatkan proxy Jerman

- **Residential:** Bright Data, IPRoyal, Smartproxy (paling aman, gak terdeteksi)
- **VPN:** Mullvad dengan exit node Jerman (gratis, tapi shared IP — bisa kena rate-limit)
- **VPS Jerman:** Hetzner, NetCup, Contabo + install SOCKS5 proxy sendiri

---

## 📋 Commands

### User

| Command | Description |
|---------|-------------|
| `/start` | Menu utama + cek status |
| `/gift @username` | Gift premium — bot tampilkan inline keyboard pilih durasi |
| `/list` | Riwayat gift kamu |

### Admin

| Command | Description |
|---------|-------------|
| `/stats` | Statistik: total gift, success rate, user aktif |
| `/reload` | Reload `.env` tanpa restart bot |
| `/cancel` | Force-cancel gift yang sedang berjalan |

---

## 🗂 Struktur

```
giftX/
├── bot.py                  # Entry point — setup PTB app, register handlers
├── config.py               # Env loader + constants
├── .env.example            # Template
├── requirements.txt        # Dependencies
│
├── handlers/
│   ├── __init__.py
│   ├── start.py            # /start, /help — menu + onboarding
│   ├── gift.py             # /gift parser + inline keyboard callback
│   └── list.py             # History viewer
│
├── xploit/
│   ├── __init__.py
│   ├── browser.py          # Nodriver setup + X login flow + 2FA handler
│   ├── gift_flow.py        # Core: navigasi profil → klik gift → payment → submit
│   └── proxy.py            # Proxy config builder
│
├── data/
│   ├── giftx.db            # SQLite — history, stats
│   └── screenshots/        # Auto-screenshot tiap gift
│
└── assets/
    └── logo.png            # Logo
```

---

## 🗄 Database Schema

```sql
CREATE TABLE gifts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id    INTEGER NOT NULL,        -- user Telegram yang trigger
    target      TEXT    NOT NULL,        -- @username target
    duration    TEXT    NOT NULL,        -- '3', '6', atau '12'
    status      TEXT    DEFAULT 'pending', -- pending|success|failed
    error       TEXT,                     -- error message jika failed
    screenshot  TEXT,                     -- path screenshot
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin ON gifts(admin_id);
CREATE INDEX idx_status ON gifts(status);
```

---

## 🔧 Troubleshooting

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `Tombol gift tidak ditemukan` | Akun A bukan premium, atau Akun B sudah premium | Pastikan Akun A verified, Akun B fresh |
| `Opsi Bank Transfer tidak muncul` | IP bukan Jerman | Cek `curl ifconfig.me` via proxy — harus return IP DE |
| `429 Too Many Requests` | IP atau akun di-rate-limit X | Rotate proxy, ganti akun A, tunggu 15-30 menit |
| `Login gagal — challenge` | X deteksi login mencurigakan | Buka akun A manual 1x dari IP yg sama sebelum pake bot |
| `Browser crash / OOM` | RAM VPS kurang | Browser butuh ~300MB — pastikan VPS minimal 1GB |
| `nodriver timeout` | Proxy lambat / Chromium gagal download | Install Chromium manual: `apt install chromium` |

---

## 🖼 Logo Prompt

```
Modern flat vector logo for "giftX" tool.
A gift box with an X-shaped ribbon merging the Twitter/X brand.
Two-tone: deep blue (#1D9BF0) gift box + white (#FFFFFF) ribbon on dark background (#0F1419).
Clean geometric shapes, no gradients, no glow, no 3D effects.
Style: minimalist tech startup icon.
```

Simpan hasil generate di `assets/logo.png`.

---

## 📸 Screenshots

<p align="center">
  <sub>Flow: /gift → pilih durasi → success</sub>
  <br>
  <sub><i>(screenshots coming soon — generate sendiri setelah setup)</i></sub>
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="version">
</p>

<p align="center">
  <sub>By mmoaa</sub>
</p>
