#!/bin/bash

set -e

INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_USER="${SUDO_USER:-$USER}"
INSTALL_GROUP="$(id -gn "$INSTALL_USER")"
VENV_DIR="${VENV_DIR:-/home/$INSTALL_USER/.env}"

sudo apt-get install -y python3-pip python3-dev python3-venv
if [ ! -d "$VENV_DIR" ]; then
    sudo -u "$INSTALL_USER" python3 -m venv "$VENV_DIR"
fi
sudo -u "$INSTALL_USER" "$VENV_DIR/bin/python" -m pip install --upgrade pip
sudo -u "$INSTALL_USER" "$VENV_DIR/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"

SERVICE_FILE="$(mktemp)"
sed \
    -e "s|^User=.*|User=$INSTALL_USER|g" \
    -e "s|^Group=.*|Group=$INSTALL_GROUP|g" \
    -e "s|^WorkingDirectory=.*|WorkingDirectory=$INSTALL_DIR|g" \
    -e "s|^ExecStart=.*|ExecStart=$VENV_DIR/bin/python $INSTALL_DIR/server.py|g" \
    "$INSTALL_DIR/unicorn-water.service" > "$SERVICE_FILE"
sudo install -m 0644 "$SERVICE_FILE" /etc/systemd/system/unicorn-water.service
rm "$SERVICE_FILE"
sudo systemctl daemon-reload
if systemctl list-unit-files busylight.service > /dev/null 2>&1; then
    sudo systemctl disable --now busylight.service
fi
if systemctl list-unit-files unicorn-solar.service > /dev/null 2>&1; then
    sudo systemctl disable --now unicorn-solar.service
fi
sudo systemctl enable --now unicorn-water.service

sudo chmod +x "$INSTALL_DIR/start.sh"
