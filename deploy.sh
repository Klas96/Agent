#!/bin/bash
set -e

# PocketFlow Deployment Script
# Deploys changes from development (/home/klas/PocketFlow) to production (/opt/pocketflow)

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
DEV_DIR="/home/klas/PocketFlow"
PROD_DIR="/opt/pocketflow"
SERVICE_NAME="pocketflow"
BACKUP_DIR="$PROD_DIR/backups"

print_header "PocketFlow Deployment Script"
print_status "Deploying from development to production..."

# Check if we're in the development directory
if [ ! -f "$DEV_DIR/main.py" ]; then
    print_error "Development directory not found: $DEV_DIR"
    exit 1
fi

# Check if production directory exists
if [ ! -d "$PROD_DIR" ]; then
    print_error "Production directory not found: $PROD_DIR"
    print_status "Run install-system.sh first to create production installation"
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
    print_status "Service is running, will restart after deployment"
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

# Deploy files
print_header "Deploying Files"
print_status "Copying application files..."

# Copy main application files
sudo cp "$DEV_DIR/main.py" "$PROD_DIR/"
sudo cp "$DEV_DIR/nodes.py" "$PROD_DIR/"
sudo cp "$DEV_DIR/flow.py" "$PROD_DIR/"

# Copy utils directory
sudo cp -r "$DEV_DIR/utils/"* "$PROD_DIR/utils/"

# Copy configuration files
sudo cp "$DEV_DIR/.env" "$PROD_DIR/" 2>/dev/null || print_warning ".env not found in dev"

# Set proper permissions
print_status "Setting permissions..."
sudo chown -R pocketflow:pocketflow "$PROD_DIR"

# Test the deployment
print_header "Testing Deployment"
print_status "Testing basic functionality..."

# Test imports
if sudo -u pocketflow /opt/pocketflow/venv/bin/python -c "
import sys
sys.path.append('/opt/pocketflow')
try:
    from utils.llm_utils import call_llm
    print('✓ LLM utils working')
except Exception as e:
    print(f'✗ LLM utils error: {e}')
    exit(1)
" 2>/dev/null; then
    print_status "✓ Basic imports working"
else
    print_error "✗ Import issues detected"
    print_status "Restoring from backup..."
    sudo tar -xzf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C "$PROD_DIR"
    exit 1
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

# Print deployment summary
print_header "Deployment Summary"
cat << EOM

🎉 PocketFlow Deployment Complete!

📁 Development: $DEV_DIR
🏢 Production: $PROD_DIR
🔧 Service: $SERVICE_NAME
📦 Backup: $BACKUP_NAME.tar.gz

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

print_status "Deployment completed successfully!" 