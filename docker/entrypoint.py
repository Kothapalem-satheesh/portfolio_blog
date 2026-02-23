import os
import socket
import subprocess
import sys
import time


def _wait_for_tcp(host: str, port: int, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while True:
        try:
            with socket.create_connection((host, port), timeout=3):
                return
        except OSError:
            if time.time() > deadline:
                raise
            time.sleep(1)


def _env_bool(key: str, default: str = "False") -> bool:
    val = os.getenv(key, default)
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def _maybe_create_or_reset_superuser() -> None:
    if not _env_bool("AUTO_CREATE_SUPERUSER", "False"):
        return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME", "") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL", "") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
    reset_password = _env_bool("AUTO_RESET_SUPERUSER_PASSWORD", "False")
    if not username or not password:
        return

    try:
        import django
        from django.contrib.auth import get_user_model

        django.setup()
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
    except Exception:
        # Never block container start
        return


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and "sqlite" not in db_url:
        # Minimal parsing to avoid surprises; docker-compose uses db:5432
        host = os.getenv("DB_HOST", "db")
        port = int(os.getenv("DB_PORT", "5432"))
        print(f"Waiting for database {host}:{port}...", flush=True)
        _wait_for_tcp(host, port, timeout_s=60)
        print("Database is up.", flush=True)

    run_migrations = _env_bool("RUN_MIGRATIONS", "True")
    if run_migrations:
        subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=False)
        subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=False)
        _maybe_create_or_reset_superuser()

    if len(sys.argv) <= 1:
        return 0

    os.execvp(sys.argv[1], sys.argv[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

