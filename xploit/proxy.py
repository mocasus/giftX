"""Proxy management — German proxy for X.com payment region."""

import os
from config import PROXY_URL

def get_proxy_config():
    """Parse PROXY_URL into nodriver-compatible proxy config."""
    if not PROXY_URL:
        return None
    
    # Format: http://user:pass@host:port or socks5://user:pass@host:port
    url = PROXY_URL
    proto = "http"
    if "://" in url:
        proto, rest = url.split("://", 1)
    else:
        rest = url
    
    auth = ""
    if "@" in rest:
        auth, hostport = rest.split("@", 1)
    else:
        hostport = rest
    
    host, port = hostport.split(":")
    port = int(port)
    
    if ":" in auth:
        user, pwd = auth.split(":", 1)
    else:
        user, pwd = "", ""
    
    return {
        "server": f"{proto}://{host}:{port}",
        "username": user,
        "password": pwd,
    }

def get_proxy_arg():
    """Return --proxy-server arg for Chrome."""
    cfg = get_proxy_config()
    if not cfg:
        return None
    return cfg["server"]
