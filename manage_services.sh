#!/bin/bash

# PocketFlow Service Management Script
# Manages the PocketFlow agent service

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

# Service names
AGENT_SERVICE="pocketflow"
SERVICES=("$AGENT_SERVICE")

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Show service status
show_status() {
    print_header "Service Status"
    
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service"; then
            print_status "✅ $service: RUNNING"
        else
            print_error "❌ $service: STOPPED"
        fi
    done
    
    echo ""
    print_status "Service Details:"
    systemctl status "$AGENT_SERVICE" --no-pager -l
}

# Start services
start_services() {
    print_header "Starting Services"
    
    for service in "${SERVICES[@]}"; do
        print_status "Starting $service..."
        systemctl start "$service"
        
        if systemctl is-active --quiet "$service"; then
            print_status "✅ $service started successfully"
        else
            print_error "❌ $service failed to start"
        fi
    done
}

# Stop services
stop_services() {
    print_header "Stopping Services"
    
    for service in "${SERVICES[@]}"; do
        print_status "Stopping $service..."
        systemctl stop "$service"
        print_status "✅ $service stopped"
    done
}

# Restart services
restart_services() {
    print_header "Restarting Services"
    
    for service in "${SERVICES[@]}"; do
        print_status "Restarting $service..."
        systemctl restart "$service"
        
        if systemctl is-active --quiet "$service"; then
            print_status "✅ $service restarted successfully"
        else
            print_error "❌ $service failed to restart"
        fi
    done
}

# Enable services
enable_services() {
    print_header "Enabling Services"
    
    for service in "${SERVICES[@]}"; do
        print_status "Enabling $service..."
        systemctl enable "$service"
        print_status "✅ $service enabled"
    done
}

# Disable services
disable_services() {
    print_header "Disabling Services"
    
    for service in "${SERVICES[@]}"; do
        print_status "Disabling $service..."
        systemctl disable "$service"
        print_status "✅ $service disabled"
    done
}

# Show logs
show_logs() {
    local service="$1"
    
    if [ -z "$service" ]; then
        print_header "Recent Logs"
        echo ""
        print_status "PocketFlow Agent logs:"
        journalctl -u "$AGENT_SERVICE" --no-pager -n 20
    else
        print_header "Logs for $service"
        journalctl -u "$service" -f
    fi
}

# Check service health
check_health() {
    print_header "Service Health Check"
    
    # Check if services are running
    local all_healthy=true
    
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service"; then
            print_status "✅ $service: Healthy"
        else
            print_error "❌ $service: Unhealthy"
            all_healthy=false
        fi
    done
    
    # Check database
    if [ -f "/opt/pocketflow/data/pocketflow.db" ]; then
        print_status "✅ Database: /opt/pocketflow/data/pocketflow.db exists"
    else
        print_error "❌ Database: /opt/pocketflow/data/pocketflow.db missing"
        all_healthy=false
    fi
    
    # Check virtual environment
    if [ -d "/opt/pocketflow/venv/bin" ]; then
        print_status "✅ Virtual Environment: /opt/pocketflow/venv exists"
    else
        print_error "❌ Virtual Environment: /opt/pocketflow/venv missing"
        all_healthy=false
    fi
    
    echo ""
    if [ "$all_healthy" = true ]; then
        print_status "🎉 All services are healthy!"
    else
        print_error "⚠️ Some issues detected. Check logs for details."
    fi
}

# Show usage
show_usage() {
    cat << EOF
PocketFlow Service Management Script

Usage: $0 [COMMAND]

Commands:
    status          Show service status
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    enable          Enable services to start on boot
    disable         Disable services from starting on boot
    logs [SERVICE]  Show logs (follow mode if SERVICE specified)
    health          Check service health
    help            Show this help message

Services:
    $AGENT_SERVICE          PocketFlow Email Agent

Examples:
    sudo $0 status          # Show status of all services
    sudo $0 start           # Start all services
    sudo $0 logs            # Show recent logs
    sudo $0 logs $AGENT_SERVICE  # Follow agent logs
    sudo $0 health          # Check service health

EOF
}

# Main script logic
main() {
    case "${1:-help}" in
        status)
            show_status
            ;;
        start)
            check_root
            start_services
            ;;
        stop)
            check_root
            stop_services
            ;;
        restart)
            check_root
            restart_services
            ;;
        enable)
            check_root
            enable_services
            ;;
        disable)
            check_root
            disable_services
            ;;
        logs)
            show_logs "$2"
            ;;
        health)
            check_health
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 