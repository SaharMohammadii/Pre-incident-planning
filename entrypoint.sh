#!/usr/bin/env bash
set -e

# Keep the shell tolerant to missing fa_IR on some base layers
export LANG=${LANG:-C.UTF-8}
export LC_ALL=${LC_ALL:-C.UTF-8}

cd /app

# Figure out where manage.py lives (/app/manage.py or /app/firestation/manage.py)
APP_DIR="/app"
if [ -f "/app/firestation/manage.py" ]; then
  APP_DIR="/app/firestation"
elif [ -f "/app/manage.py" ]; then
  APP_DIR="/app"
else
  echo "manage.py not found under /app or /app/firestation. Contents:"
  ls -la /app
  exit 1
fi

# Ensure static root exists and is writable; then hand ownership to appuser
mkdir -p /app/staticfiles || true
chown -R appuser:appuser /app/staticfiles || true
chmod -R 775 /app/staticfiles || true

# Wait for Postgres
python - <<'PY'
import os, time, psycopg2
host=os.getenv("POSTGRES_HOST","db")
port=int(os.getenv("POSTGRES_PORT","5432"))
user=os.getenv("POSTGRES_USER","app")
pwd=os.getenv("POSTGRES_PASSWORD","app")
db=os.getenv("POSTGRES_DB","app")
for i in range(180):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db).close()
        print("DB is ready")
        break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("DB not reachable")
PY

# Run Django tasks as non-root
cd "$APP_DIR"
su -s /bin/bash -c "export DJANGO_SETTINGS_MODULE=firestation.settings; python manage.py migrate --noinput" appuser
su -s /bin/bash -c "export DJANGO_SETTINGS_MODULE=firestation.settings; python manage.py collectstatic --noinput" appuser

# Optional: auto-create superuser if env present
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  su -s /bin/bash -c "export DJANGO_SETTINGS_MODULE=firestation.settings; python manage.py createsuperuser --noinput || true" appuser
fi

# Start Gunicorn as non-root
exec su -s /bin/bash -c "export DJANGO_SETTINGS_MODULE=firestation.settings; gunicorn firestation.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 90" appuser
