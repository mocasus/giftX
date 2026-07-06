"""Core gift exploit flow — automated X Premium gifting via bank transfer."""

import asyncio
import time
import os
from datetime import datetime
from pathlib import Path
from xploit.browser import create_browser, login_x, safe_close

# German address for bank transfer form
GERMAN_ADDRESS = {
    "first_name": "Max",
    "last_name": "Müller",
    "street": "Hauptstraße 42",
    "city": "Berlin",
    "zip": "10115",
    "country": "DE",
}

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

async def run_gift(target_username: str, user_id: int) -> dict:
    """
    Execute the gift exploit flow.
    
    Returns: {"success": bool, "error": str, "screenshot": str}
    """
    browser = None
    result = {"success": False, "error": "", "screenshot": ""}
    
    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        
        browser = await create_browser(headless=True)
        page = await browser.get("https://x.com/login")
        
        # 1. Login as Akun A (premium)
        logged_in = await login_x(browser, page)
        if not logged_in:
            result["error"] = "Login gagal — periksa kredensial Akun A"
            return result
        
        await page.sleep(3)
        
        # 2. Navigate to target profile
        profile_url = f"https://x.com/{target_username.lstrip('@')}"
        await page.get(profile_url)
        await page.sleep(5)
        
        # Screenshot profile
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ss_path = str(SCREENSHOT_DIR / f"gift_{user_id}_{ts}.png")
        
        # 3. Click gift icon (🎁)
        gift_clicked = False
        buttons = await page.query_selector_all("div[role='button']")
        for btn in buttons:
            text = await btn.text_content()
            if "🎁" in text or "gift" in text.lower() or "hadiah" in text.lower():
                await btn.click()
                gift_clicked = True
                break
        
        if not gift_clicked:
            # Try aria-label
            gift_btn = await page.query_selector("[aria-label*='Gift'], [aria-label*='gift']")
            if gift_btn:
                await gift_btn.click()
                gift_clicked = True
        
        if not gift_clicked:
            result["error"] = "Tombol gift tidak ditemukan — Akun A mungkin tidak premium"
            return result
        
        await page.sleep(5)
        
        # 4. Select X Premium plan
        # Look for premium tier selection
        plan_selected = False
        for btn in await page.query_selector_all("div[role='button']"):
            text = await btn.text_content()
            if "premium" in text.lower() or "x premium" in text.lower():
                await btn.click()
                plan_selected = True
                break
        
        if not plan_selected:
            # Try to find any continue/next button
            for btn in await page.query_selector_all("div[role='button']"):
                text = await btn.text_content()
                if "next" in text.lower() or "continue" in text.lower() or "lanjut" in text.lower():
                    await btn.click()
                    break
        
        await page.sleep(5)
        
        # 5. Select Bank Transfer payment
        payment_selected = False
        payment_texts = ["bank transfer", "bank", "sepa", "überweisung", "bank transfer"]
        for btn in await page.query_selector_all("div[role='button'], label, span"):
            text = (await btn.text_content()).lower()
            for pt in payment_texts:
                if pt in text:
                    await btn.click()
                    payment_selected = True
                    break
            if payment_selected:
                break
        
        if not payment_selected:
            result["error"] = "Opsi Bank Transfer tidak muncul — pastikan VPN Jerman aktif"
            return result
        
        await page.sleep(5)
        
        # 6. Fill address form
        await _fill_german_address(page)
        await page.sleep(3)
        
        # 7. Click Continue/Submit
        for btn in await page.query_selector_all("div[role='button']"):
            text = (await btn.text_content()).lower()
            if "continue" in text or "submit" in text or "weiter" in text:
                await btn.click()
                break
        
        await page.sleep(8)
        
        # 8. Invoice should appear — take screenshot
        os.makedirs(os.path.dirname(ss_path) if os.path.dirname(ss_path) else ".", exist_ok=True)
        await page.save_screenshot(ss_path)
        result["screenshot"] = ss_path
        
        # Check for success indicators
        page_text = await page.evaluate("() => document.body.innerText")
        success_keywords = ["invoice", "bank transfer", "rechnung", "überweisung", "thank you", "vielen dank"]
        
        if any(kw in page_text.lower() for kw in success_keywords):
            result["success"] = True
            result["error"] = ""
        else:
            result["error"] = "Invoice tidak muncul — flow mungkin berubah"
        
        return result
        
    except Exception as e:
        result["error"] = f"Error: {str(e)}"
        return result
    finally:
        if browser:
            await safe_close(browser)

async def _fill_german_address(page):
    """Fill billing address with German data."""
    # Common form field selectors
    field_map = {
        "first name": GERMAN_ADDRESS["first_name"],
        "vorname": GERMAN_ADDRESS["first_name"],
        "last name": GERMAN_ADDRESS["last_name"],
        "nachname": GERMAN_ADDRESS["last_name"],
        "address": GERMAN_ADDRESS["street"],
        "adresse": GERMAN_ADDRESS["street"],
        "street": GERMAN_ADDRESS["street"],
        "straße": GERMAN_ADDRESS["street"],
        "city": GERMAN_ADDRESS["city"],
        "stadt": GERMAN_ADDRESS["city"],
        "ort": GERMAN_ADDRESS["city"],
        "zip": GERMAN_ADDRESS["zip"],
        "plz": GERMAN_ADDRESS["zip"],
        "postal": GERMAN_ADDRESS["zip"],
    }
    
    inputs = await page.query_selector_all("input")
    for inp in inputs:
        name = (await inp.get_attribute("name") or "").lower()
        autocomplete = (await inp.get_attribute("autocomplete") or "").lower()
        placeholder = (await inp.get_attribute("placeholder") or "").lower()
        label = ""
        
        # Try to find associated label
        inp_id = await inp.get_attribute("id")
        if inp_id:
            label_el = await page.query_selector(f"label[for='{inp_id}']")
            if label_el:
                label = (await label_el.text_content()).lower()
        
        search_text = f"{name} {autocomplete} {placeholder} {label}"
        
        for keyword, value in field_map.items():
            if keyword in search_text:
                await inp.fill(value)
                break
