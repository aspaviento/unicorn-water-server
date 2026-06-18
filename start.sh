#!/usr/bin/env sh
set -eu

VENV_DIR="${VENV_DIR:-/home/pi/.env}"

if [ -n "${VIRTUAL_ENV:-}" ]; then
    exec python3 ./server.py
fi

if [ -x "$VENV_DIR/bin/python" ]; then
    exec "$VENV_DIR/bin/python" ./server.py
fi

exec python3 ./server.py
