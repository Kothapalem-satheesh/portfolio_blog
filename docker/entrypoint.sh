#!/usr/bin/env sh
set -eu

if [ "${DATABASE_URL:-}" != "" ]; then
  echo "Waiting for database..."
  python - <<'PY'
import os
import time
import dj_database_url

cfg = dj_database_url.parse(os.environ["DATABASE_URL"])
engine = cfg.get("ENGINE", "")

if engine.endswith("sqlite3"):
    raise SystemExit(0)

host = cfg.get("HOST") or "db"
port = int(cfg.get("PORT") or 5432)

deadline = time.time() + 60
while True:
    try:
        import socket
        with socket.create_connection((host, port), timeout=3):
            break
    except OSError:
        if time.time() > deadline:
            raise
        time.sleep(1)
print("Database is up.")
PY
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec "$@"

