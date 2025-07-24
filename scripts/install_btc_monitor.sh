#!/bin/bash

# Install and start BTC Payment Monitor service
# This script installs the systemd service for automatic BTC payment monitoring

set -e

echo "🔧 Installing BTC Payment Monitor Service..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Define paths
SERVICE_FILE="btc_payment_monitor.service"
SERVICE_NAME="btc-payment-monitor"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Project root: $PROJECT_ROOT"

# Copy service file to systemd directory
echo "📋 Installing systemd service..."
cp "$SCRIPT_DIR/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_NAME.service"

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Enable and start the service
echo "🚀 Starting BTC payment monitor service..."
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Check service status
echo "📊 Checking service status..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "✅ BTC Payment Monitor service is running successfully!"
    echo "📝 Service logs: journalctl -u $SERVICE_NAME -f"
    echo "🛑 To stop: sudo systemctl stop $SERVICE_NAME"
    echo "🔄 To restart: sudo systemctl restart $SERVICE_NAME"
else
    echo "❌ Failed to start BTC Payment Monitor service"
    echo "📝 Check logs: journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

echo ""
echo "🎉 BTC Payment Monitor installation complete!"
echo "💡 The service will automatically monitor for BTC payments and credit tokens" 