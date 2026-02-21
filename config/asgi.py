import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_asgi_application()


def _env_bool(key: str, default: str = "False") -> bool:
    val = os.getenv(key, default)
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def _maybe_create_superuser() -> None:
    if not _env_bool("AUTO_CREATE_SUPERUSER", "False"):
        return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME", "") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL", "") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
    reset_password = _env_bool("AUTO_RESET_SUPERUSER_PASSWORD", "False")
    if not username or not password:
        return

    try:
        from django.contrib.auth import get_user_model
        from django.db import OperationalError, ProgrammingError

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user:
            if reset_password:
                user.set_password(password)
                if email:
                    user.email = email
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return
        User.objects.create_superuser(username=username, email=email, password=password)
    except (OperationalError, ProgrammingError):
        return
    except Exception:
        return


_maybe_create_superuser()
