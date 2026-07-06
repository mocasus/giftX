"""nodriver browser wrapper for X.com automation."""

import asyncio
import nodriver as uc
from config import X_EMAIL, X_PASSWORD, X_2FA_SECRET
import pyotp

STEALTH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=ChromeWhatsNewUI",
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
]

async def create_browser(headless: bool = True):
    """Create a stealth nodriver browser instance."""
    browser = await uc.start(
        headless=headless,
        browser_args=STEALTH_ARGS,
    )
    return browser

async def login_x(browser, page=None) -> bool:
    """Login to X.com with credentials + 2FA."""
    if page is None:
        page = await browser.get("https://x.com/login")
    
    await page.sleep(3)
    
    # Step 1: Enter email
    email_input = await page.select("input[autocomplete='username']")
    if email_input:
        await email_input.send_keys(X_EMAIL)
        await page.sleep(1)
        # Click Next
        next_btns = await page.select_all("div[role='button']")
        for btn in next_btns:
            text = btn.text_all.lower() if hasattr(btn, 'text_all') else ""
            if "next" in text or "lanjut" in text:
                await btn.click()
                break
        await page.sleep(3)
    
    # Step 2: Handle verification if asked (username/phone)
    verify_input = await page.select("input[data-testid='ocfEnterTextTextInput']")
    if verify_input:
        # X asks for username/phone verification
        await verify_input.send_keys(X_EMAIL.split("@")[0])
        await page.sleep(1)
        for btn in await page.select_all("div[role='button']"):
            text = btn.text_all.lower() if hasattr(btn, 'text_all') else ""
            if "next" in text:
                await btn.click()
                break
        await page.sleep(3)
    
    # Step 3: Enter password
    pwd_input = await page.select("input[name='password']")
    if pwd_input:
        await pwd_input.send_keys(X_PASSWORD)
        await page.sleep(1)
        # Click Log in
        for btn in await page.select_all("div[role='button']"):
            text = btn.text_all.lower() if hasattr(btn, 'text_all') else ""
            if "log in" in text or "masuk" in text:
                await btn.click()
                break
        await page.sleep(5)
    
    # Step 4: 2FA if configured
    if X_2FA_SECRET:
        otp_input = await page.select("input[data-testid='ocfEnterTextTextInput']")
        if otp_input:
            totp = pyotp.TOTP(X_2FA_SECRET)
            code = totp.now()
            await otp_input.send_keys(code)
            await page.sleep(1)
            for btn in await page.select_all("div[role='button']"):
                text = btn.text_all.lower() if hasattr(btn, 'text_all') else ""
                if "next" in text or "confirm" in text:
                    await btn.click()
                    break
            await page.sleep(5)
    
    # Verify logged in
    await page.sleep(3)
    url = page.target.url if hasattr(page.target, 'url') else ""
    return "x.com/home" in url or "twitter.com/home" in url

async def safe_close(browser):
    """Safely close browser."""
    try:
        await browser.stop()
    except:
        pass
