import os

from .base import *  # noqa: F403,F401

DEBUG = False

# ── Cache: use Redis if available, else in-memory (free tier) ──
_redis_url = os.getenv("REDIS_URL", "")
if _redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _redis_url,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "prod-cache",
        }
    }

# ── Security ────────────────────────────────────────────────────
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Auto-include the Render URL + any custom domains
_render_url = os.getenv("RENDER_EXTERNAL_URL", "")
_extra_origins = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "")
_origins = [o.strip() for o in _extra_origins.split(",") if o.strip()]
if _render_url and _render_url not in _origins:
    _origins.append(_render_url)
CSRF_TRUSTED_ORIGINS = _origins

# Also add render domain to ALLOWED_HOSTS automatically
_render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME", "")
if _render_hostname and _render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_render_hostname)

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
