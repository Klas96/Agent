#!/bin/bash

# PocketFlow Control Panel Runner
# This script starts the web-based control panel for user management

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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "This script must be run from the PocketFlow directory"
    exit 1
fi

print_header "PocketFlow Control Panel"
print_status "Starting web-based control panel..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
elif [ -d "/opt/pocketflow/venv" ]; then
    print_status "Activating production virtual environment..."
    source /opt/pocketflow/venv/bin/activate
else
    print_warning "No virtual environment found. Using system Python."
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export CONTROL_PANEL_HOST="${CONTROL_PANEL_HOST:-0.0.0.0}"
export CONTROL_PANEL_PORT="${CONTROL_PANEL_PORT:-5000}"
export CONTROL_PANEL_DEBUG="${CONTROL_PANEL_DEBUG:-false}"

print_status "Configuration:"
print_status "  Host: $CONTROL_PANEL_HOST"
print_status "  Port: $CONTROL_PANEL_PORT"
print_status "  Debug: $CONTROL_PANEL_DEBUG"

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    print_warning "Flask not found. Installing dependencies..."
    pip install flask flask-cors
fi

# Start the control panel
print_status "Starting control panel..."
python control_panel.py 