#!/bin/bash
# RaspberryMeet - Service Management Helper
# Simple script to manage RaspberryMeet systemd services

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Services
ORCHESTRATOR="raspberrymeet.service"
WEB="raspberrymeet-web.service"
KIOSK="raspberrymeet-kiosk.service"

ALL_SERVICES=("$ORCHESTRATOR" "$WEB" "$KIOSK")

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This command requires sudo"
        exit 1
    fi
}

service_exists() {
    systemctl list-unit-files | grep -q "$1"
}

service_status() {
    local service="$1"

    if ! service_exists "$service"; then
        echo -e "${YELLOW}Not Installed${NC}"
        return
    fi

    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}Running${NC}"
    elif systemctl is-enabled --quiet "$service"; then
        echo -e "${YELLOW}Stopped (Enabled)${NC}"
    else
        echo -e "${RED}Stopped (Disabled)${NC}"
    fi
}

show_status() {
    print_header "RaspberryMeet Services Status"

    echo "Service                          Status"
    echo "────────────────────────────────────────────────────────"
    printf "%-30s   %s\n" "Orchestrator (GPIO + Browser)" "$(service_status $ORCHESTRATOR)"
    printf "%-30s   %s\n" "Web Interface" "$(service_status $WEB)"
    printf "%-30s   %s\n" "Kiosk Display" "$(service_status $KIOSK)"
    echo ""
}

start_services() {
    check_sudo
    print_header "Starting Services"

    for service in "${ALL_SERVICES[@]}"; do
        if service_exists "$service"; then
            print_info "Starting $service..."
            systemctl start "$service"
            if systemctl is-active --quiet "$service"; then
                print_success "$service started"
            else
                print_error "$service failed to start"
            fi
        fi
    done
}

stop_services() {
    check_sudo
    print_header "Stopping Services"

    for service in "${ALL_SERVICES[@]}"; do
        if service_exists "$service"; then
            print_info "Stopping $service..."
            systemctl stop "$service"
            print_success "$service stopped"
        fi
    done
}

restart_services() {
    check_sudo
    print_header "Restarting Services"

    for service in "${ALL_SERVICES[@]}"; do
        if service_exists "$service"; then
            print_info "Restarting $service..."
            systemctl restart "$service"
            if systemctl is-active --quiet "$service"; then
                print_success "$service restarted"
            else
                print_error "$service failed to restart"
            fi
        fi
    done
}

enable_services() {
    check_sudo
    print_header "Enabling Services for Autostart"

    for service in "${ALL_SERVICES[@]}"; do
        if service_exists "$service"; then
            print_info "Enabling $service..."
            systemctl enable "$service"
            print_success "$service enabled"
        fi
    done
}

disable_services() {
    check_sudo
    print_header "Disabling Services from Autostart"

    for service in "${ALL_SERVICES[@]}"; do
        if service_exists "$service"; then
            print_info "Disabling $service..."
            systemctl disable "$service"
            print_success "$service disabled"
        fi
    done
}

view_logs() {
    local service="$1"

    if [[ -z "$service" ]]; then
        echo "Available services:"
        echo "  1) orchestrator"
        echo "  2) web"
        echo "  3) kiosk"
        echo ""
        read -p "Select service (1-3): " choice

        case $choice in
            1) service="$ORCHESTRATOR" ;;
            2) service="$WEB" ;;
            3) service="$KIOSK" ;;
            *) print_error "Invalid choice"; exit 1 ;;
        esac
    fi

    print_info "Showing logs for $service (Ctrl+C to exit)"
    echo ""
    sudo journalctl -u "$service" -f
}

show_menu() {
    print_header "RaspberryMeet Service Manager"
    echo "1) Show Status"
    echo "2) Start All Services"
    echo "3) Stop All Services"
    echo "4) Restart All Services"
    echo "5) Enable Autostart"
    echo "6) Disable Autostart"
    echo "7) View Logs"
    echo "8) Exit"
    echo ""
    read -p "Enter your choice: " choice

    case $choice in
        1) show_status; show_menu ;;
        2) start_services; show_menu ;;
        3) stop_services; show_menu ;;
        4) restart_services; show_menu ;;
        5) enable_services; show_menu ;;
        6) disable_services; show_menu ;;
        7) view_logs; show_menu ;;
        8) echo ""; print_info "Goodbye!"; echo ""; exit 0 ;;
        *) print_error "Invalid choice"; show_menu ;;
    esac
}

# Main
if [[ $# -eq 0 ]]; then
    # Interactive mode
    show_menu
else
    # Command line mode
    case "$1" in
        status) show_status ;;
        start) start_services ;;
        stop) stop_services ;;
        restart) restart_services ;;
        enable) enable_services ;;
        disable) disable_services ;;
        logs) view_logs "$2" ;;
        *)
            echo "Usage: $0 {status|start|stop|restart|enable|disable|logs [service]}"
            echo ""
            echo "Examples:"
            echo "  $0 status              - Show service status"
            echo "  $0 start               - Start all services"
            echo "  $0 stop                - Stop all services"
            echo "  $0 restart             - Restart all services"
            echo "  $0 enable              - Enable autostart"
            echo "  $0 disable             - Disable autostart"
            echo "  $0 logs                - View logs (interactive)"
            echo "  $0 logs orchestrator   - View orchestrator logs"
            exit 1
            ;;
    esac
fi
