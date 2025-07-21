#!/bin/bash
set -e

APP_NAME="pocketflow"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="pocketflow"
SERVICE_GROUP="pocketflow"

echo "Uninstalling PocketFlow..."

# Stop and disable service
systemctl stop $APP_NAME.service || true
systemctl disable $APP_NAME.service || true

# Remove service file
rm -f /etc/systemd/system/$APP_NAME.service

# Remove logrotate configuration
rm -f /etc/logrotate.d/$APP_NAME

# Reload systemd
systemctl daemon-reload

# Remove application files
rm -rf $APP_DIR

# Remove logs (optional - uncomment if you want to keep logs)
# rm -rf /var/log/$APP_NAME

# Remove configuration (optional - uncomment if you want to keep config)
# rm -rf /etc/$APP_NAME

# Remove user and group (optional - uncomment if you want to remove them)
# userdel $SERVICE_USER || true
# groupdel $SERVICE_GROUP || true

echo "PocketFlow has been uninstalled."
