#!/bin/bash
# RaspberryMeet - Install systemd services
# This script installs and enables the systemd services for autostart

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="$(pwd)"
SERVICE_DIR="${INSTALL_DIR}/systemd"
USER="${USER:-pi}"
GROUP="${USER}"

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_directory() {
    if [[ ! -d "${SERVICE_DIR}" ]]; then
        print_error "Service directory not found: ${SERVICE_DIR}"
        print_info "Make sure you're running this from the RaspberryMeet directory"
        exit 1
    fi
}

install_service() {
    local service_file="$1"
    local service_name=$(basename "${service_file}")

    print_info "Installing ${service_name}..."

    # Update paths in service file for current installation
    sed "s|/home/pi/RaspberryMeet|${INSTALL_DIR}|g" "${service_file}" > "/tmp/${service_name}"
    sed -i "s|User=pi|User=${USER}|g" "/tmp/${service_name}"
    sed -i "s|Group=pi|Group=${GROUP}|g" "/tmp/${service_name}"

    # Copy to systemd directory
    cp "/tmp/${service_name}" "/etc/systemd/system/${service_name}"
    rm "/tmp/${service_name}"

    print_success "${service_name} installed"
}

enable_service() {
    local service_name="$1"

    print_info "Enabling ${service_name}..."
    systemctl daemon-reload
    systemctl enable "${service_name}"

    print_success "${service_name} enabled"
}

start_service() {
    local service_name="$1"

    print_info "Starting ${service_name}..."
    systemctl start "${service_name}"

    # Check status
    if systemctl is-active --quiet "${service_name}"; then
        print_success "${service_name} started successfully"
    else
        print_warning "${service_name} failed to start - check logs with: journalctl -u ${service_name} -f"
    fi
}

configure_user_permissions() {
    print_header "Configuring User Permissions"

    # Add user to gpio group for GPIO access
    if getent group gpio > /dev/null 2>&1; then
        usermod -a -G gpio "${USER}"
        print_success "User ${USER} added to gpio group"
    else
        print_warning "gpio group not found - GPIO may not work"
    fi

    # Add user to video group for camera access
    if getent group video > /dev/null 2>&1; then
        usermod -a -G video "${USER}"
        print_success "User ${USER} added to video group"
    else
        print_warning "video group not found"
    fi
}

# Main installation
main() {
    print_header "RaspberryMeet Service Installation"

    # Checks
    check_root
    check_directory

    print_info "Installation directory: ${INSTALL_DIR}"
    print_info "User: ${USER}"
    print_info "Group: ${GROUP}"
    echo ""

    # Configure permissions
    configure_user_permissions

    # Ask which services to install
    print_header "Select Services to Install"
    echo ""
    echo "Available services:"
    echo "  1) raspberrymeet.service       - Main orchestrator (GPIO + Browser)"
    echo "  2) raspberrymeet-web.service   - Web admin interface"
    echo "  3) raspberrymeet-kiosk.service - Kiosk display (optional)"
    echo "  4) All services"
    echo ""
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            SERVICES=("raspberrymeet.service")
            ;;
        2)
            SERVICES=("raspberrymeet-web.service")
            ;;
        3)
            SERVICES=("raspberrymeet-kiosk.service")
            ;;
        4)
            SERVICES=("raspberrymeet.service" "raspberrymeet-web.service" "raspberrymeet-kiosk.service")
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac

    # Install services
    print_header "Installing Services"
    for service in "${SERVICES[@]}"; do
        install_service "${SERVICE_DIR}/${service}"
    done

    # Enable services
    print_header "Enabling Services"
    for service in "${SERVICES[@]}"; do
        enable_service "${service}"
    done

    # Ask to start now
    echo ""
    read -p "Start services now? (y/n): " start_now

    if [[ "$start_now" =~ ^[Yy]$ ]]; then
        print_header "Starting Services"
        for service in "${SERVICES[@]}"; do
            start_service "${service}"
        done
    else
        print_info "Services will start on next boot"
        print_info "To start manually: sudo systemctl start <service-name>"
    fi

    # Summary
    print_header "Installation Complete"
    echo ""
    print_success "Services installed and enabled!"
    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status <service-name>   - Check service status"
    echo "  sudo systemctl start <service-name>    - Start service"
    echo "  sudo systemctl stop <service-name>     - Stop service"
    echo "  sudo systemctl restart <service-name>  - Restart service"
    echo "  sudo journalctl -u <service-name> -f   - View logs"
    echo ""
    echo "Installed services:"
    for service in "${SERVICES[@]}"; do
        echo "  - ${service}"
    done
    echo ""

    if [[ "$start_now" =~ ^[Yy]$ ]]; then
        print_info "Services are running. Check status with:"
        echo ""
        for service in "${SERVICES[@]}"; do
            echo "  sudo systemctl status ${service}"
        done
    else
        print_warning "Remember to reboot or start services manually!"
    fi

    echo ""
}

# Run main installation
main
