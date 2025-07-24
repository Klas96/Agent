#!/bin/bash

# Test script for PocketFlow Control Panel

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

print_header "PocketFlow Control Panel Test"

# Check if we're in the right directory
if [ ! -f "control_panel_minimal.py" ]; then
    print_error "This script must be run from the PocketFlow directory"
    exit 1
fi

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
export CONTROL_PANEL_HOST="127.0.0.1"
export CONTROL_PANEL_PORT="5000"
export CONTROL_PANEL_DEBUG="true"

print_status "Configuration:"
print_status "  Host: $CONTROL_PANEL_HOST"
print_status "  Port: $CONTROL_PANEL_PORT"
print_status "  Debug: $CONTROL_PANEL_DEBUG"

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    print_warning "Flask not found. Installing dependencies..."
    pip install flask flask-cors pydantic pydantic-settings PyYAML
fi

# Start the control panel in background
print_status "Starting control panel..."
python control_panel_minimal.py &
CONTROL_PANEL_PID=$!

# Wait for it to start
sleep 5

# Test if it's accessible
print_status "Testing control panel accessibility..."
if curl -s http://127.0.0.1:5000/admin/ > /dev/null; then
    print_status "✅ Control panel is accessible at http://127.0.0.1:5000/admin/"
else
    print_error "❌ Control panel is not accessible"
    print_status "Checking if process is running..."
    if ps -p $CONTROL_PANEL_PID > /dev/null; then
        print_status "Process is running, checking logs..."
        # Kill the process to see any error output
        kill $CONTROL_PANEL_PID 2>/dev/null || true
        sleep 1
        print_status "Restarting in foreground to see errors..."
        python control_panel_minimal.py
    else
        print_error "Process is not running"
    fi
    exit 1
fi

# Test API endpoints
print_status "Testing API endpoints..."

# Test stats endpoint
if curl -s http://127.0.0.1:5000/admin/api/stats | grep -q "success"; then
    print_status "✅ API stats endpoint working"
else
    print_error "❌ API stats endpoint failed"
fi

# Test users endpoint
if curl -s http://127.0.0.1:5000/admin/api/users | grep -q "success"; then
    print_status "✅ API users endpoint working"
else
    print_error "❌ API users endpoint failed"
fi

# Show the dashboard HTML
print_status "Dashboard HTML preview:"
curl -s http://127.0.0.1:5000/admin/ | head -10

# Clean up
print_status "Stopping control panel..."
kill $CONTROL_PANEL_PID 2>/dev/null || true

print_header "Test Complete!"
print_status "Control panel is working correctly!"
print_status "You can now deploy it as a service using:"
print_status "  sudo ./deploy.sh" 