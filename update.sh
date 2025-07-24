#!/bin/bash
set -e

# PocketFlow Update Script
# Updates the production system with latest changes

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

# Configuration
PROD_DIR="/opt/pocketflow"
SERVICE_NAME="pocketflow"
BACKUP_DIR="$PROD_DIR/backups"

print_header "PocketFlow Update Script"
print_status "Starting update process..."

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "This script must be run from the PocketFlow directory"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="pocketflow_backup_$BACKUP_TIMESTAMP"

print_header "Creating Backup"
print_status "Creating backup: $BACKUP_NAME"

# Backup production files
sudo tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    --exclude="venv" \
    --exclude="__pycache__" \
    --exclude="backups" \
    --exclude="*.pyc" \
    -C "$PROD_DIR" .

print_status "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Check if service is running
print_header "Checking Service Status"
if systemctl is-active $SERVICE_NAME >/dev/null 2>&1; then
    print_status "Service is running, will restart after update"
    SERVICE_RUNNING=true
else
    print_status "Service is not running"
    SERVICE_RUNNING=false
fi

# Stop service if running
if [ "$SERVICE_RUNNING" = true ]; then
    print_status "Stopping service..."
    sudo systemctl stop $SERVICE_NAME
    sleep 2
fi

# Update Python dependencies
print_header "Updating Dependencies"
print_status "Activating virtual environment..."
source "$PROD_DIR/venv/bin/activate"

print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Updating Python dependencies..."
# Install torch first (compatible with python3.12)
pip install torch==2.7.1

# Install all other dependencies except torch, audiocraft, and julius
if [ -f "requirements.txt" ]; then
    grep -v -E '^(torch|audiocraft|julius)' requirements.txt > requirements-no-torch.txt
    pip install -r requirements-no-torch.txt --upgrade
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip install numpy soundfile openai google-generativeai anthropic requests python-dotenv --upgrade
fi

# Install audiocraft and julius with --no-deps if needed
print_status "Updating audio processing dependencies..."
pip install --no-deps audiocraft julius --upgrade 2>/dev/null || print_warning "audiocraft/julius update skipped"

# Update startup script
print_header "Updating Startup Script"
cat > "$PROD_DIR/run_app.sh" << 'EOF'
#!/bin/bash
source /opt/pocketflow/venv/bin/activate
cd /opt/pocketflow
export PYTHONPATH="${PYTHONPATH}:/opt/pocketflow/src"
exec python main.py
EOF
chmod +x "$PROD_DIR/run_app.sh"

# Update systemd service
print_header "Updating Systemd Service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=PocketFlow Email Agent and BTC Service
After=network.target

[Service]
Type=simple
User=pocketflow
WorkingDirectory=$PROD_DIR
ExecStart=$PROD_DIR/run_app.sh
Restart=on-failure
RestartSec=10
Environment=PYTHONPATH=$PROD_DIR:$PROD_DIR/src
Environment=BTC_SHARED_PATH=$PROD_DIR/data/shared.yaml
EnvironmentFile=$PROD_DIR/.env

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
print_status "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Run tests to ensure everything works
print_header "Running Update Tests"
print_status "Testing basic functionality..."

# Test imports for new modular architecture
if python -c "
import sys
sys.path.append('.')
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
    exit 1
fi

# Test music generation (legacy support)
if python -c "
import sys
sys.path.append('.')
try:
    from utils.generate_sound import generate_sound
    print('✓ Music generation working')
except Exception as e:
    print(f'✗ Music generation error: {e}')
    print('Note: This is legacy functionality, new system uses content service')
" 2>/dev/null; then
    print_status "✓ Music generation working"
else
    print_warning "Music generation not available (legacy functionality)"
fi

# Start service if it was running before
if [ "$SERVICE_RUNNING" = true ]; then
    print_header "Restarting Service"
    print_status "Starting service..."
    sudo systemctl start $SERVICE_NAME
    
    # Wait a moment and check status
    sleep 3
    if systemctl is-active $SERVICE_NAME >/dev/null 2>&1; then
        print_status "✓ Service started successfully"
    else
        print_error "✗ Service failed to start"
        print_status "Check logs with: journalctl -u $SERVICE_NAME -f"
    fi
else
    print_status "Service was not running, not starting it"
fi

# Clean up old backups (keep last 5)
print_header "Cleaning Up"
BACKUP_COUNT=$(sudo ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    print_status "Removing old backups (keeping last 5)..."
    sudo ls -t "$BACKUP_DIR"/*.tar.gz | tail -n +6 | sudo xargs rm -f
fi

# Print update summary
print_header "Update Summary"
cat << EOM

🎉 PocketFlow Update Complete!

📁 Application Directory: $PROD_DIR
🔧 Service Name: $SERVICE_NAME
📦 Backup Created: $BACKUP_NAME.tar.gz

📋 Service Status:
EOM

if systemctl is-active $SERVICE_NAME >/dev/null 2>&1; then
    echo "✓ Service is running"
else
    echo "⚠ Service is not running"
fi

cat << EOM

📊 Useful Commands:
- Check status: sudo systemctl status $SERVICE_NAME
- View logs: journalctl -u $SERVICE_NAME -f
- Restart service: sudo systemctl restart $SERVICE_NAME
- Stop service: sudo systemctl stop $SERVICE_NAME

🔄 Rollback (if needed):
- Stop service: sudo systemctl stop $SERVICE_NAME
- Restore backup: sudo tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $PROD_DIR
- Restart service: sudo systemctl start $SERVICE_NAME

EOM

print_status "Update completed successfully!" 