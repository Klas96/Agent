#!/bin/bash
set -e

# Configuration
APP_NAME="pocketflow"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="pocketflow"
SERVICE_GROUP="pocketflow"
VENV_DIR="/opt/$APP_NAME/venv"
LOG_DIR="/var/log/$APP_NAME"
CONFIG_DIR="/etc/$APP_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Starting PocketFlow system installation..."

# 1. Create service user and group
print_status "Creating service user and group..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    print_status "Created user: $SERVICE_USER"
else
    print_status "User $SERVICE_USER already exists"
fi

# 2. Create directories
print_status "Creating directories..."
mkdir -p "$APP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$APP_DIR/data"

# 3. Copy application files
print_status "Copying application files..."
cp -r . "$APP_DIR/"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
chmod -R 755 "$APP_DIR"

# 4. Create Python virtual environment
print_status "Creating Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    print_status "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi
python3 -m venv "$VENV_DIR"
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    print_error "Virtual environment creation failed!"
    exit 1
fi
print_status "Virtual environment created successfully"

# 5. Activate venv and install dependencies
print_status "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"

# Install torch first (compatible with python3.12 and audiocraft)
pip install torch==2.7.1

# Install all other Python dependencies except torch, audiocraft, and julius
grep -v -E '^(torch|audiocraft|julius)' requirements.txt > "$APP_DIR/requirements-no-torch.txt"
pip install -r "$APP_DIR/requirements-no-torch.txt"

# Install audiocraft and julius with --no-deps
pip install --no-deps audiocraft julius

# Ensure requests is installed for BTC price fetching
pip install requests python-dotenv

# 6. Create startup script
print_status "Creating startup script..."
cat > "$APP_DIR/run_app.sh" << 'EOF'
#!/bin/bash
source /opt/pocketflow/venv/bin/activate
cd /opt/pocketflow
exec python main.py
EOF

chmod +x "$APP_DIR/run_app.sh"
chown "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR/run_app.sh"

# 7. Create systemd service file
print_status "Creating systemd service..."
cat > "/etc/systemd/system/$APP_NAME.service" << EOF
[Unit]
Description=PocketFlow Email Agent and BTC Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/run_app.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

# Environment variables
Environment=BTC_SHARED_PATH=$APP_DIR/data/shared.yaml
Environment=PYTHONPATH=$APP_DIR

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/data $LOG_DIR

[Install]
WantedBy=multi-user.target
EOF

# 8. Create logrotate configuration
print_status "Creating logrotate configuration..."
cat > "/etc/logrotate.d/$APP_NAME" << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload $APP_NAME.service >/dev/null 2>&1 || true
    endscript
}
EOF

# 9. Set proper permissions
print_status "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$CONFIG_DIR"
chmod 755 "$LOG_DIR"
chmod 755 "$CONFIG_DIR"

# 10. Reload systemd and enable service
print_status "Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable "$APP_NAME.service"

# 11. Create configuration template
print_status "Creating configuration template..."
cat > "$CONFIG_DIR/config.yaml" << 'EOF'
# PocketFlow Configuration
# Copy this file to your desired location and update the values

# Application settings
app:
  name: "PocketFlow"
  version: "1.0.0"
  log_level: "INFO"

# Database settings (if applicable)
database:
  path: "/opt/pocketflow/data/user_data.db"

# API settings (if applicable)
api:
  host: "localhost"
  port: 8080

# BTC settings
btc:
  shared_path: "/opt/pocketflow/data/shared.yaml"
  wallet_path: "/opt/pocketflow/data/wallet"
EOF

chown "$SERVICE_USER:$SERVICE_GROUP" "$CONFIG_DIR/config.yaml"
chmod 644 "$CONFIG_DIR/config.yaml"

# 12. Create uninstall script
print_status "Creating uninstall script..."
cat > "$APP_DIR/uninstall.sh" << 'EOF'
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
EOF

chmod +x "$APP_DIR/uninstall.sh"

# 13. Print installation summary
print_status "Installation complete!"
echo
echo "=== PocketFlow System Installation Summary ==="
echo "Application Directory: $APP_DIR"
echo "Service User: $SERVICE_USER"
echo "Log Directory: $LOG_DIR"
echo "Config Directory: $CONFIG_DIR"
echo "Virtual Environment: $VENV_DIR"
echo
echo "=== Service Management ==="
echo "Start service:     systemctl start $APP_NAME"
echo "Stop service:      systemctl stop $APP_NAME"
echo "Restart service:   systemctl restart $APP_NAME"
echo "Check status:      systemctl status $APP_NAME"
echo "View logs:         journalctl -u $APP_NAME -f"
echo
echo "=== Configuration ==="
echo "Edit configuration: $CONFIG_DIR/config.yaml"
echo "Application data:   $APP_DIR/data/"
echo
echo "=== Uninstallation ==="
echo "To uninstall:      $APP_DIR/uninstall.sh"
echo
print_warning "The service is installed but not started. Run 'systemctl start $APP_NAME' to start it."
print_warning "Make sure to configure your environment variables and BTC wallet settings before starting." 