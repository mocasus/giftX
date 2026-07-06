"""nodriver browser wrapper for X.com automation."""

import asyncio
import logging
import nodriver as uc
from config import X_EMAIL, X_PASSWORD, X_2FA_SECRET
import pyotp

logger = logging.getLogger(__name__)

STEALTH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=ChromeWhatsNewUI",
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
]


def _text(el):
    """Safely get text from a nodriver element (sync property or async)."""
    try:
        t = el.text_all
        if asyncio.iscoroutine(t):
            return ""
        return (t or "").lower()
    except Exception:
        return ""


async def _find_click(page, keywords: list[str]) -> bool:
    """Find and click a button containing any keyword."""
    for btn in await page.query_selector_all("div[role='button'], button"):
        text = _text(btn)
        if any(kw.lower() in text for kw in keywords):
            try:
                await btn.click()
                return True
            except Exception:
                continue
    # Fallback: evaluate JS
    for kw in keywords:
        try:
            el = await page.evaluate(
                f"""() => {{
                    const btns = document.querySelectorAll("div[role='button'], button");
                    for (const b of btns) {{
                        if ((b.textContent || '').toLowerCase().includes('{kw.lower()}')) {{
                            b.click();
                            return true;
                        }}
                    }}
                    return false;
                }}"""
            )
            if el:
                return True
        except Exception:
            continue
    return False


async def create_browser(headless: bool = True):
    """Create a stealth nodriver browser instance."""
    logger.info("Starting nodriver browser (headless=%s)...", headless)
    browser = await uc.start(
        headless=headless,
        browser_args=STEALTH_ARGS,
    )
    logger.info("Browser started OK")
    return browser


async def login_x(browser, page=None) -> bool:
    """Login to X.com with credentials + 2FA."""
    if page is None:
        page = await browser.get("https://x.com/login")

    await page.sleep(3)
    logger.info("Starting X login flow...")

    # Step 1: Enter email
    email_input = await page.select("input[autocomplete='username']")
    if email_input:
        logger.info("Found email input, typing...")
        await email_input.send_keys(X_EMAIL)
        await page.sleep(1)
        await _find_click(page, ["next", "lanjut", "berikut"])
        await page.sleep(3)
    else:
        logger.warning("Email input not found")

    # Step 2: Handle verification if asked (username/phone)
    verify_input = await page.select("input[data-testid='ocfEnterTextTextInput']")
    if verify_input:
        logger.info("Verification screen detected, typing username...")
        await verify_input.send_keys(X_EMAIL.split("@")[0])
        await page.sleep(1)
        await _find_click(page, ["next", "lanjut"])
        await page.sleep(3)

    # Step 3: Enter password
    pwd_input = await page.select("input[name='password']")
    if pwd_input:
        logger.info("Found password input, typing...")
        await pwd_input.send_keys(X_PASSWORD)
        await page.sleep(1)
        await _find_click(page, ["log in", "masuk", "sign in"])
        await page.sleep(5)
    else:
        logger.warning("Password input not found")

    # Step 4: 2FA if configured
    if X_2FA_SECRET:
        otp_input = await page.select("input[data-testid='ocfEnterTextTextInput']")
        if otp_input:
            logger.info("2FA prompt detected, sending OTP...")
            totp = pyotp.TOTP(X_2FA_SECRET)
            code = totp.now()
            await otp_input.send_keys(code)
            await page.sleep(1)
            await _find_click(page, ["next", "confirm"])
            await page.sleep(5)

    # Verify logged in
    await page.sleep(3)
    url = page.target.url if hasattr(page.target, 'url') else ""
    logged_in = "x.com/home" in url or "twitter.com/home" in url
    logger.info("Login %s (URL: %s)", "OK" if logged_in else "FAILED", url[:80])
    return logged_in


async def safe_close(browser):
    """Safely close browser."""
    try:
        await browser.stop()
    except Exception:
        pass
