#!/bin/bash

# PocketFlow Deployment Script
# This script deploys PocketFlow with the control panel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_header "PocketFlow Deployment with Control Panel"

# Create pocketflow user if it doesn't exist
if ! id "pocketflow" &>/dev/null; then
    print_status "Creating pocketflow user..."
    useradd -r -s /bin/false -d /opt/pocketflow pocketflow
fi

# Create directories
print_status "Creating directories..."
mkdir -p /opt/pocketflow/{src,data,logs,venv}
mkdir -p /opt/pocketflow/src/pocketflow/{core,nodes,services,flows,config,utils,web}

# Set permissions
chown -R pocketflow:pocketflow /opt/pocketflow
chmod -R 755 /opt/pocketflow

# Copy source files
print_status "Copying source files..."
cp -r src/* /opt/pocketflow/src/
cp main.py /opt/pocketflow/
cp control_panel.py /opt/pocketflow/
cp flow.py /opt/pocketflow/
cp requirements.txt /opt/pocketflow/

# Set ownership
chown -R pocketflow:pocketflow /opt/pocketflow

# Create virtual environment if it doesn't exist
if [ ! -d "/opt/pocketflow/venv/bin" ]; then
    print_status "Creating virtual environment..."
    sudo -u pocketflow python3 -m venv /opt/pocketflow/venv
fi

# Install dependencies
print_status "Installing Python dependencies..."
sudo -u pocketflow /opt/pocketflow/venv/bin/pip install --upgrade pip
sudo -u pocketflow /opt/pocketflow/venv/bin/pip install flask flask-cors pydantic pydantic-settings PyYAML

# Install PocketFlow dependencies (minimal set for control panel)
print_status "Installing PocketFlow dependencies..."
sudo -u pocketflow /opt/pocketflow/venv/bin/pip install openai anthropic google-generativeai requests

# Create database if it doesn't exist
if [ ! -f "/opt/pocketflow/data/pocketflow.db" ]; then
    print_status "Initializing database..."
    sudo -u pocketflow /opt/pocketflow/venv/bin/python -c "
import sqlite3
import os
os.makedirs('/opt/pocketflow/data', exist_ok=True)
conn = sqlite3.connect('/opt/pocketflow/data/pocketflow.db')
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    name TEXT,
    personality TEXT,
    tokens INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create btc_addresses table
cursor.execute('''
CREATE TABLE IF NOT EXISTS btc_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    address TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email)
)
''')

# Create payment_transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    amount_btc REAL NOT NULL,
    amount_usd REAL NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email) REFERENCES users(email)
)
''')



conn.commit()
conn.close()
print('Database initialized successfully')
"
fi

# Install systemd services
print_status "Installing systemd services..."

# Main PocketFlow service
cat > /etc/systemd/system/pocketflow.service << 'EOF'
[Unit]
Description=PocketFlow Email Processing Agent
After=network.target

[Service]
Type=simple
User=pocketflow
Group=pocketflow
WorkingDirectory=/opt/pocketflow
Environment=PATH=/opt/pocketflow/venv/bin
Environment=PYTHONPATH=/opt/pocketflow/src
ExecStart=/opt/pocketflow/venv/bin/python /opt/pocketflow/main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/pocketflow/data /opt/pocketflow/logs

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pocketflow

[Install]
WantedBy=multi-user.target
EOF

# Control Panel service
cat > /etc/systemd/system/pocketflow-control-panel.service << 'EOF'
[Unit]
Description=PocketFlow Control Panel
After=network.target pocketflow.service
Wants=pocketflow.service

[Service]
Type=simple
User=pocketflow
Group=pocketflow
WorkingDirectory=/opt/pocketflow
Environment=PATH=/opt/pocketflow/venv/bin
Environment=PYTHONPATH=/opt/pocketflow/src
Environment=CONTROL_PANEL_HOST=0.0.0.0
Environment=CONTROL_PANEL_PORT=5001
Environment=CONTROL_PANEL_DEBUG=false
ExecStart=/opt/pocketflow/venv/bin/python /opt/pocketflow/control_panel.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/pocketflow/data /opt/pocketflow/logs

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pocketflow-control-panel

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable and start services
print_status "Starting services..."
systemctl enable pocketflow.service
systemctl enable pocketflow-control-panel.service

# Start services
systemctl start pocketflow.service
systemctl start pocketflow-control-panel.service

# Wait a moment for services to start
sleep 5

# Check service status
print_status "Checking service status..."
if systemctl is-active --quiet pocketflow.service; then
    print_status "✅ PocketFlow service is running"
else
    print_error "❌ PocketFlow service failed to start"
    systemctl status pocketflow.service
fi

if systemctl is-active --quiet pocketflow-control-panel.service; then
    print_status "✅ PocketFlow Control Panel service is running"
else
    print_error "❌ PocketFlow Control Panel service failed to start"
    systemctl status pocketflow-control-panel.service
fi

print_header "Deployment Complete!"

print_status "Services installed and running:"
echo "  • PocketFlow Agent: http://localhost:5000 (if configured)"
echo "  • Control Panel: http://localhost:5001/admin/"
echo ""
print_status "Service management commands:"
echo "  • View status: sudo systemctl status pocketflow pocketflow-control-panel"
echo "  • Stop services: sudo systemctl stop pocketflow pocketflow-control-panel"
echo "  • Start services: sudo systemctl start pocketflow pocketflow-control-panel"
echo "  • Restart services: sudo systemctl restart pocketflow pocketflow-control-panel"
echo "  • View logs: sudo journalctl -u pocketflow -f"
echo "  • View control panel logs: sudo journalctl -u pocketflow-control-panel -f"
echo ""
print_status "Access the control panel at: http://localhost:5001/admin/"
print_status "Default port is 5001 to avoid conflicts with other services" 