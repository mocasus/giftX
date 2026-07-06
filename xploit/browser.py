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


async def _get_url(page) -> str:
    """Safe URL getter for nodriver tabs."""
    try:
        if hasattr(page, "target") and hasattr(page.target, "url"):
            return page.target.url or ""
    except Exception:
        pass
    try:
        if hasattr(page, "url"):
            u = page.url
            if not asyncio.iscoroutine(u):
                return u or ""
    except Exception:
        pass
    return ""


async def _find_click(page, keywords: list[str]) -> bool:
    """Find and click a button containing any keyword (CDP real mouse events)."""
    from nodriver.cdp import runtime, input_

    escaped_keywords = "', '".join(k.lower() for k in keywords)
    
    # Step 1: find button and get its position
    js_find = f"""(function() {{
        const keywords = ['{escaped_keywords}'];
        const all = document.querySelectorAll("div[role='button'], button, span");
        for (const el of all) {{
            if (el.offsetHeight === 0) continue;
            const t = (el.textContent || '').toLowerCase().trim();
            for (const kw of keywords) {{
                if (t === kw || t.includes(kw)) {{
                    const rect = el.getBoundingClientRect();
                    el.setAttribute('data-fox-target', 'true');
                    return JSON.stringify({{x: rect.left + rect.width/2, y: rect.top + rect.height/2, w: rect.width, h: rect.height}});
                }}
            }}
        }}
        return 'not-found';
    }})()"""

    for attempt in range(3):
        try:
            result = await page.send(runtime.evaluate(
                expression=js_find,
                return_by_value=True,
                await_promise=False,
            ))
            obj, _ = result
            val = obj.value if hasattr(obj, 'value') else None
            if not val or val == 'not-found':
                continue
            
            import json
            pos = json.loads(val)
            cx = pos['x']
            cy = pos['y']
            
            logger.debug(f"CDP mouse click at ({cx:.0f}, {cy:.0f})")
            
            # Simulate real mouse click
            await page.send(input_.dispatch_mouse_event(
                type_='mousePressed', x=cx, y=cy,
                button='left', buttons=1, click_count=1,
                pointer_type='mouse',
            ))
            await page.sleep(0.05)
            await page.send(input_.dispatch_mouse_event(
                type_='mouseReleased', x=cx, y=cy,
                button='left', buttons=0, click_count=1,
                pointer_type='mouse',
            ))
            
            logger.info(f"Clicked via CDP mouse: kw={keywords[0]} at ({cx:.0f},{cy:.0f})")
            return True
            
        except Exception as e:
            logger.debug(f"CDP mouse attempt {attempt}: {e}")
            continue

    # Fallback: CDP programmatic click
    js_click = f"""(function() {{
        const keywords = ['{escaped_keywords}'];
        const all = document.querySelectorAll("div[role='button'], button, span");
        for (const el of all) {{
            if (el.offsetHeight === 0) continue;
            const t = (el.textContent || '').toLowerCase().trim();
            for (const kw of keywords) {{
                if (t === kw || t.includes(kw)) {{
                    el.focus();
                    el.dispatchEvent(new MouseEvent('mousedown', {{bubbles: true, cancelable: true}}));
                    el.dispatchEvent(new MouseEvent('mouseup', {{bubbles: true, cancelable: true}}));
                    el.dispatchEvent(new MouseEvent('click', {{bubbles: true, cancelable: true}}));
                    return 'clicked:' + kw;
                }}
            }}
        }}
        return 'not-found';
    }})()"""
    
    for attempt in range(3):
        try:
            result = await page.send(runtime.evaluate(
                expression=js_click,
                return_by_value=True,
                await_promise=False,
            ))
            obj, _ = result
            val = obj.value if hasattr(obj, 'value') else None
            if val and 'clicked' in str(val):
                logger.info(f"CDP click fallback: {val}")
                return True
        except Exception as e:
            continue

    # Last resort: nodriver native
    for btn in await page.query_selector_all("div[role='button'], button"):
        try:
            text = (btn.text_all or "").lower()
            if any(kw.lower() in text for kw in keywords):
                await btn.click()
                return True
        except Exception:
            continue

    return False


async def _find_and_fill(page, selectors: list[str], value: str) -> bool:
    """Find an input by selectors and fill with value (CDP-based for React)."""
    from nodriver.cdp import runtime
    escaped_value = value.replace("\\", "\\\\").replace("'", "\\'")

    # CDP JS fill — triggers React onChange properly
    for sel in selectors:
        js = f"""(function() {{
            const el = document.querySelector('{sel}');
            if (!el) return 'not-found';
            el.focus();
            // Use native setter that React tracks
            const nativeSetter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;
            nativeSetter.call(el, '{escaped_value}');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return 'filled';
        }})()"""
        try:
            result = await page.send(runtime.evaluate(
                expression=js,
                return_by_value=True,
                await_promise=False,
            ))
            obj, _ = result
            val = obj.value if hasattr(obj, 'value') else None
            if val == 'filled':
                logger.info("CDP filled %s in %s", value[:20], sel)
                return True
        except Exception as e:
            logger.debug("CDP fill %s: %s", sel, e)

    # Fallback: nodriver native click + type
    for sel in selectors:
        try:
            inp = await page.query_selector(sel)
            if inp:
                await inp.click()
                await page.sleep(0.2)
                await inp.send_keys(value)
                logger.info("Native filled %s in %s", value[:20], sel)
                return True
        except Exception as e:
            logger.debug("Native fill %s: %s", sel, e)
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
    """Login to X.com — try session cookies first, fall back to password."""
    if page is None:
        page = await browser.get("https://x.com")
        await page.sleep(3)

    # === PRIMARY: Session transfer from cookies.json ===
    import json, os
    cookie_file = os.path.join(os.path.dirname(__file__), "cookies.json")
    if os.path.exists(cookie_file):
        logger.info("Found cookies.json — injecting session...")
        with open(cookie_file) as f:
            cookies = json.load(f)
        
        from nodriver.cdp import runtime
        for c in cookies:
            name = c['name']
            val = c['value']
            path = c.get('path', '/')
            secure = '; Secure' if c.get('secure') else ''
            same_site = c.get('sameSite', '')
            ss = '; SameSite=None' if same_site == 'no_restriction' else f'; SameSite={same_site.capitalize()}' if same_site else ''
            
            js = f"document.cookie = '{name}={val}; path={path}{secure}{ss}'"
            try:
                await page.send(runtime.evaluate(expression=js, return_by_value=True, await_promise=False))
            except Exception:
                continue

        await page.get("https://x.com/home")
        await page.sleep(5)
        
        # CDP URL check — more reliable than _get_url
        try:
            result = await page.send(runtime.evaluate(
                expression="location.href",
                return_by_value=True, await_promise=False))
            obj, _ = result
            url = obj.value if hasattr(obj, 'value') else ""
        except Exception:
            url = await _get_url(page)
        
        if "x.com/home" in url or "twitter.com/home" in url:
            logger.info("Session transfer OK → logged in")
            return True
        else:
            logger.warning("Session transfer to /home failed, checking timeline...")
            # CDP check for timeline
            has_tl = False
            try:
                from nodriver.cdp import runtime
                result = await page.send(runtime.evaluate(
                    expression='!!document.querySelector("[data-testid=\\"primaryColumn\\"]")',
                    return_by_value=True, await_promise=False,
                ))
                obj, _ = result
                has_tl = bool(obj.value) if hasattr(obj, 'value') else False
            except Exception:
                pass
            if has_tl:
                logger.info("Session transfer OK via timeline fallback")
                return True
            logger.warning("Session transfer FAILED — falling back to password login")

    # === FALLBACK: Password-based login ===
    await page.get("https://x.com/login")
    await page.sleep(4)
    logger.info("Starting X password login flow...")

    # Step 1: Enter email
    email_selectors = [
        "input[name='text']",
        "input[autocomplete='username']",
        "input[type='email']",
        "input[type='text']",
    ]
    filled = await _find_and_fill(page, email_selectors, X_EMAIL)
    if filled:
        await page.sleep(1)
        await _find_click(page, ["continue", "next", "lanjut", "berikut"])
        await page.sleep(4)

    # Step 2: Handle verification — X might ask for username/phone
    from nodriver.cdp import runtime
    page_text = ""
    try:
        page_text = (await page.send(runtime.evaluate(
            expression="document.body?.innerText?.toLowerCase()?.substring(0, 500) || ''",
            return_by_value=True, await_promise=False,
        ))).value
    except Exception:
        pass
    page_text = str(page_text) if page_text else ""

    if any(kw in page_text for kw in ["verify", "phone", "username", "unusual", "login code", "phone number"]):
        logger.info("Verification screen detected, trying username fill...")
        username = X_EMAIL.split("@")[0]
        # Use CDP to fill username field
        js_fill_user = f"""(function(){{
            var inp = document.querySelector("input[name='text'], input:not([type='hidden']):not([type='password'])");
            if(inp && inp.offsetHeight > 0){{
                inp.focus();
                var ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                ns.call(inp, '{username}');
                inp.dispatchEvent(new Event('input', {{bubbles:true}}));
                inp.dispatchEvent(new Event('change', {{bubbles:true}}));
                return 'filled';
            }}
            return 'no-inp';
        }})()"""
        await page.send(runtime.evaluate(expression=js_fill_user, return_by_value=True, await_promise=False))
        await page.sleep(1)
        await _find_click(page, ["next", "lanjut"])
        await page.sleep(4)

    # Step 3: Enter password
    pwd_selectors = [
        "input[name='password']",
        "input[type='password']",
    ]
    pwd_filled = await _find_and_fill(page, pwd_selectors, X_PASSWORD)
    if pwd_filled:
        await page.sleep(1)
        await _find_click(page, ["log in", "masuk", "sign in", "login"])
        await page.sleep(6)

    # Step 4: 2FA if configured
    if X_2FA_SECRET:
        try:
            result = await page.send(runtime.evaluate(
                expression='!!document.querySelector("input[data-testid=\\"ocfEnterTextTextInput\\"]")',
                return_by_value=True, await_promise=False,
            ))
            obj, _ = result
            has_otp = bool(obj.value) if hasattr(obj, 'value') else False
        except Exception:
            has_otp = False
        
        if has_otp:
            logger.info("2FA prompt detected, sending OTP...")
            totp = pyotp.TOTP(X_2FA_SECRET)
            code = totp.now()
            # CDP fill OTP
            js_fill_otp = f"""(function(){{
                var inp = document.querySelector("input[data-testid='ocfEnterTextTextInput']");
                if(!inp) return 'no-inp';
                inp.focus();
                var ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                ns.call(inp, '{code}');
                inp.dispatchEvent(new Event('input', {{bubbles:true}}));
                inp.dispatchEvent(new Event('change', {{bubbles:true}}));
                return 'filled';
            }})()"""
            await page.send(runtime.evaluate(expression=js_fill_otp, return_by_value=True, await_promise=False))
            await page.sleep(1)
            await _find_click(page, ["next", "confirm"])
            await page.sleep(5)

    # Step 5: Bypass "Save login" prompt
    await page.sleep(2)
    await _find_click(page, ["skip", "not now", "nanti"])

    # Verify logged in
    await page.sleep(3)
    url = await _get_url(page)
    logged_in = "x.com/home" in url or "twitter.com/home" in url

    if not logged_in:
        try:
            result = await page.send(runtime.evaluate(
                expression='!!document.querySelector("[data-testid=\\"primaryColumn\\"], [aria-label=\\"Timeline\\"]")',
                return_by_value=True, await_promise=False,
            ))
            obj, _ = result
            logged_in = bool(obj.value) if hasattr(obj, 'value') else False
            logger.info("Fallback login check (timeline): %s", logged_in)
        except Exception:
            pass

    logger.info("Login %s (URL: %s)", "OK" if logged_in else "FAILED", url[:80] if url else "")
    return logged_in


async def safe_close(browser):
    """Safely close browser."""
    try:
        await browser.stop()
    except Exception:
        pass
