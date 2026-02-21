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


def main() -> int:
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and "sqlite" not in db_url:
        # Minimal parsing to avoid surprises; docker-compose uses db:5432
        host = os.getenv("DB_HOST", "db")
        port = int(os.getenv("DB_PORT", "5432"))
        print(f"Waiting for database {host}:{port}...", flush=True)
        _wait_for_tcp(host, port, timeout_s=60)
        print("Database is up.", flush=True)

    subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=False)
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=False)

    if len(sys.argv) <= 1:
        return 0

    os.execvp(sys.argv[1], sys.argv[1:])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

