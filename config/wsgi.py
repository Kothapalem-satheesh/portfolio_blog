import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()


def _env_bool(key: str, default: str = "False") -> bool:
    val = os.getenv(key, default)
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def _maybe_create_superuser() -> None:
    """
    Render free tier may not allow interactive shell.
    If enabled via env vars, create a superuser on startup.
    """
    if not _env_bool("AUTO_CREATE_SUPERUSER", "False"):
        return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME", "") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL", "") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
    if not username or not password:
        return

    try:
        import logging

        from django.contrib.auth import get_user_model
        from django.db import OperationalError, ProgrammingError

        logger = logging.getLogger(__name__)
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        logger.info("Auto-created superuser username=%s", username)
    except (OperationalError, ProgrammingError):
        # DB not ready / migrations not applied yet
        return
    except Exception:
        # Never block app boot because of this helper
        return


_maybe_create_superuser()
