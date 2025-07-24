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
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_header "PocketFlow System Installation"
print_status "Installing PocketFlow with new modular architecture..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "This script must be run from the PocketFlow directory"
    exit 1
fi

# Check if new architecture exists
if [ ! -d "src" ]; then
    print_error "New modular architecture (src/) not found"
    print_error "Please ensure the new architecture is properly set up"
    exit 1
fi

# 1. Create service user and group
print_header "Creating Service User"
print_status "Creating service user and group..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    print_status "Created user: $SERVICE_USER"
else
    print_status "User $SERVICE_USER already exists"
fi

# 2. Create directories
print_header "Creating Directories"
print_status "Creating directories..."
mkdir -p "$APP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$APP_DIR/data"
mkdir -p "$APP_DIR/backups"

# 3. Copy application files
print_header "Copying Application Files"
print_status "Copying application files..."
cp -r . "$APP_DIR/"
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR"
chmod -R 755 "$APP_DIR"

# 4. Create Python virtual environment
print_header "Setting Up Python Environment"
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
print_header "Installing Dependencies"
print_status "Installing Python dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install pydantic-settings for new architecture
print_status "Installing new architecture dependencies..."
pip install pydantic-settings

# Install torch first (compatible with python3.12 and audiocraft)
print_status "Installing PyTorch..."
pip install torch==2.7.1

# Install all other Python dependencies except torch, audiocraft, and julius
print_status "Installing other dependencies..."
grep -v -E '^(torch|audiocraft|julius)' requirements.txt > "$APP_DIR/requirements-no-torch.txt"
pip install -r "$APP_DIR/requirements-no-torch.txt"

# Install audiocraft and julius with --no-deps
print_status "Installing audio processing dependencies..."
pip install --no-deps audiocraft julius

# Ensure requests is installed for BTC price fetching
pip install requests python-dotenv

# 6. Create startup script for new architecture
print_header "Creating Startup Script"
print_status "Creating startup script..."
cat > "$APP_DIR/run_app.sh" << 'EOF'
#!/bin/bash
source /opt/pocketflow/venv/bin/activate
cd /opt/pocketflow
export PYTHONPATH="${PYTHONPATH}:/opt/pocketflow/src"
exec python main.py
EOF
chmod +x "$APP_DIR/run_app.sh"
chown "$SERVICE_USER:$SERVICE_GROUP" "$APP_DIR/run_app.sh"

# 7. Create systemd service file for new architecture
print_header "Creating Systemd Service"
print_status "Creating systemd service..."
cat > "/etc/systemd/system/$APP_NAME.service" << EOF
[Unit]
Description=PocketFlow Email Agent and BTC Service (New Architecture)
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/run_app.sh
Restart=on-failure
RestartSec=10
Environment=PYTHONPATH=$APP_DIR:$APP_DIR/src
Environment=BTC_SHARED_PATH=$APP_DIR/data/shared.yaml
EnvironmentFile=$APP_DIR/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$APP_NAME

[Install]
WantedBy=multi-user.target
EOF

# 8. Test the installation
print_header "Testing Installation"
print_status "Testing new architecture..."

# Test imports for new modular architecture
if sudo -u "$SERVICE_USER" "$VENV_DIR/bin/python" -c "
import sys
sys.path.append('$APP_DIR')
try:
    from src.pocketflow import flow_manager, get_settings
    print('✓ New modular architecture working')
except Exception as e:
    print(f'✗ New architecture error: {e}')
    exit(1)
" 2>/dev/null; then
    print_status "✓ New modular architecture working"
else
    print_error "✗ New architecture issues detected"
    print_status "Please check the installation and try again"
    exit 1
fi

# 9. Initialize database
print_header "Initializing Database"
print_status "Setting up database..."
sudo -u "$SERVICE_USER" "$VENV_DIR/bin/python" -c "
import sys
sys.path.append('$APP_DIR')
try:
    from src.pocketflow.services.database_service import database_service
    print('✓ Database service initialized')
except Exception as e:
    print(f'Database initialization error: {e}')
" 2>/dev/null || print_warning "Database initialization had issues (this is normal for first run)"

# 10. Reload systemd and enable service
print_header "Enabling Service"
print_status "Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable "$APP_NAME"

# 11. Print installation summary
print_header "Installation Summary"
cat << EOM

🎉 PocketFlow Installation Complete!

📁 Application Directory: $APP_DIR
👤 Service User: $SERVICE_USER
🔧 Service Name: $APP_NAME
🏗️ Architecture: New Modular (src/pocketflow/)

📋 Service Status:
EOM

if systemctl is-enabled "$APP_NAME" >/dev/null 2>&1; then
    echo "✓ Service is enabled"
else
    echo "⚠ Service is not enabled"
fi

cat << EOM

📊 Useful Commands:
- Start service: sudo systemctl start $APP_NAME
- Check status: sudo systemctl status $APP_NAME
- View logs: journalctl -u $APP_NAME -f
- Restart service: sudo systemctl restart $APP_NAME
- Stop service: sudo systemctl stop $APP_NAME

🔧 Configuration:
- Edit config: $CONFIG_DIR/
- View logs: $LOG_DIR/
- Data directory: $APP_DIR/data/

🏗️ New Architecture Features:
- Modular design with src/pocketflow/
- Service layer abstraction
- Improved error handling
- Better configuration management
- Database service integration

EOM

print_status "Installation completed successfully!" 