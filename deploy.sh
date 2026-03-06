#!/bin/bash
# Deploy PocketFlow Email Agent to production

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

# Configuration
APP_NAME="pocketflow"
APP_DIR="/opt/$APP_NAME"
SERVICE_USER="pocketflow"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if running from correct directory
if [ ! -f "main.py" ]; then
    print_error "This script must be run from the EmailAgent1 directory"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_header "Deploying PocketFlow Email Agent"
print_status "Source directory: $SOURCE_DIR"
print_status "Target directory: $APP_DIR"

# Check if production directory exists
if [ ! -d "$APP_DIR" ]; then
    print_warning "Production directory $APP_DIR does not exist"
    print_status "Running initial installation..."
    if [ -f "$SOURCE_DIR/install-system.sh" ]; then
        "$SOURCE_DIR/install-system.sh"
    else
        print_error "install-system.sh not found. Please run install-system.sh first."
        exit 1
    fi
fi

# Backup existing data and venv
print_header "Backing Up Existing Installation"
if [ -d "$APP_DIR/data" ]; then
    print_status "Backing up data directory..."
    sudo cp -r "$APP_DIR/data" "$APP_DIR/data.backup.$(date +%Y%m%d_%H%M%S)" || print_warning "Could not backup data directory"
fi

# Copy application files
print_header "Copying Application Files"
print_status "Copying source code..."
sudo cp -r src/ "$APP_DIR/"
sudo cp -r templates/ "$APP_DIR/" 2>/dev/null || print_warning "templates/ directory not found"
sudo cp -r config/ "$APP_DIR/" 2>/dev/null || print_warning "config/ directory not found"
sudo cp -r utils/ "$APP_DIR/" 2>/dev/null || print_warning "utils/ directory not found"

# Copy essential files
print_status "Copying essential files..."
sudo cp main.py "$APP_DIR/"
sudo cp requirements.txt "$APP_DIR/"
sudo cp run_app.sh "$APP_DIR/" 2>/dev/null || print_warning "run_app.sh not found"

# Copy service files if they exist
if [ -d "scripts/services" ]; then
    print_status "Copying systemd service files..."
    sudo cp scripts/services/*.service /etc/systemd/system/ 2>/dev/null || print_warning "Could not copy service files"
fi

# Set permissions
print_header "Setting Permissions"
print_status "Setting ownership and permissions..."
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"
sudo chmod +x "$APP_DIR/run_app.sh" 2>/dev/null || true
sudo chmod +x "$APP_DIR/main.py" 2>/dev/null || true

# Install/update dependencies
print_header "Installing/Updating Dependencies"
if [ ! -d "$APP_DIR/venv" ]; then
    print_status "Creating virtual environment..."
    sudo -u "$SERVICE_USER" python3 -m venv "$APP_DIR/venv"
fi

print_status "Updating Python dependencies..."
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" || print_warning "Some dependencies may have failed to install"

# Verify installation
print_header "Verifying Installation"
print_status "Testing imports..."
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$APP_DIR/src')
try:
    from src.pocketflow import flow_manager
    from src.pocketflow.config.settings import get_settings
    print('✅ Core imports successful')
except Exception as e:
    print(f'❌ Core import failed: {e}')
    sys.exit(1)
" || print_error "Import verification failed"

# Test podcastify tool if available
print_status "Testing podcastify tool..."
sudo -u "$SERVICE_USER" "$APP_DIR/venv/bin/python" -c "
import sys
sys.path.insert(0, '$APP_DIR/src')
try:
    from src.pocketflow.tools.podcastify import PodcastifyTool
    tool = PodcastifyTool()
    print('✅ PodcastifyTool imported successfully')
except Exception as e:
    print(f'⚠️  PodcastifyTool import failed (may be optional): {e}')
" || print_warning "Podcastify tool test failed (may be optional)"

# Reload systemd and restart services
print_header "Restarting Services"
print_status "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Restart main service
if systemctl list-unit-files | grep -q "^${APP_NAME}.service"; then
    print_status "Restarting $APP_NAME service..."
    sudo systemctl restart "$APP_NAME" || print_warning "Failed to restart $APP_NAME service"
    
    # Wait a moment and check status
    sleep 2
    if systemctl is-active --quiet "$APP_NAME"; then
        print_status "✅ $APP_NAME service is running"
    else
        print_error "❌ $APP_NAME service failed to start"
        print_status "Check logs with: sudo journalctl -u $APP_NAME -n 50"
    fi
else
    print_warning "$APP_NAME service not found. You may need to run install-system.sh first."
fi


# Final status
print_header "Deployment Summary"
print_status "✅ Deployment completed!"
print_status ""
print_status "Application directory: $APP_DIR"
print_status "Service user: $SERVICE_USER"
print_status ""
print_status "Useful commands:"
print_status "  Check status: sudo systemctl status $APP_NAME"
print_status "  View logs: sudo journalctl -u $APP_NAME -f"
print_status "  Restart: sudo systemctl restart $APP_NAME"
print_status "  Manage services: sudo $SOURCE_DIR/manage_services.sh status"
