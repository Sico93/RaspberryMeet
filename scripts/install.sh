#!/bin/bash
#
# RaspberryMeet Installation Script
# One-command setup for complete RaspberryMeet installation
#
# Usage: sudo ./scripts/install.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${INSTALL_DIR:-/home/pi/RaspberryMeet}"
PI_USER="${SUDO_USER:-pi}"
PI_HOME="/home/${PI_USER}"

# Installation options (can be overridden)
INSTALL_DISPLAY="${INSTALL_DISPLAY:-yes}"
INSTALL_SERVICES="${INSTALL_SERVICES:-yes}"
INSTALL_KIOSK="${INSTALL_KIOSK:-yes}"
AUTO_REBOOT="${AUTO_REBOOT:-no}"

# Logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Print header
print_header() {
    clear
    echo ""
    echo "========================================================================"
    echo "  🍓 RaspberryMeet Installation"
    echo "========================================================================"
    echo ""
    echo "  BigBlueButton Meeting Room on Raspberry Pi"
    echo ""
    echo "  This script will install and configure:"
    echo "    • System dependencies (Python, Chromium, X11)"
    echo "    • Python virtual environment"
    echo "    • RaspberryMeet application"
    echo "    • Kiosk mode (fullscreen browser)"
    echo "    • Systemd services (autostart)"
    echo "    • GPIO, Audio, Calendar integration"
    echo ""
    echo "========================================================================"
    echo ""
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi

    if [ -z "$SUDO_USER" ]; then
        log_error "Please run with sudo, not as root user directly"
        exit 1
    fi

    log_info "Running as root with user: $PI_USER"
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    log_step "Checking system..."

    if [ -f /proc/device-tree/model ]; then
        MODEL=$(cat /proc/device-tree/model)
        log_info "Detected: $MODEL"

        # Check if Raspberry Pi 4 or newer
        if [[ $MODEL == *"Raspberry Pi 4"* ]] || [[ $MODEL == *"Raspberry Pi 5"* ]]; then
            log_success "Raspberry Pi 4/5 detected - optimal performance"
        elif [[ $MODEL == *"Raspberry Pi 3"* ]]; then
            log_warn "Raspberry Pi 3 detected - may have limited performance"
        else
            log_warn "Older Raspberry Pi detected - performance may be limited"
        fi
    else
        log_warn "Not running on Raspberry Pi (or detection failed)"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check disk space
check_disk_space() {
    log_step "Checking disk space..."

    AVAILABLE=$(df / | tail -1 | awk '{print $4}')
    AVAILABLE_GB=$((AVAILABLE / 1024 / 1024))

    if [ $AVAILABLE_GB -lt 2 ]; then
        log_error "Insufficient disk space. Need at least 2GB free."
        log_error "Available: ${AVAILABLE_GB}GB"
        exit 1
    fi

    log_success "Disk space OK: ${AVAILABLE_GB}GB available"
}

# Update system
update_system() {
    log_step "Updating system packages..."

    apt-get update -qq
    apt-get upgrade -y -qq

    log_success "System updated"
}

# Install system dependencies
install_dependencies() {
    log_step "Installing system dependencies..."

    # Core dependencies
    PACKAGES=(
        # Python
        python3
        python3-pip
        python3-venv
        python3-dev

        # Build tools
        build-essential
        git
        curl
        wget

        # Audio/Video
        pulseaudio
        pulseaudio-utils
        alsa-utils
        v4l-utils

        # Bluetooth
        bluez
        bluez-tools

        # X11 and display
        xserver-xorg
        x11-xserver-utils
        xinit
        openbox
        lightdm
        unclutter
        xdotool

        # Browser
        chromium-browser

        # System utilities
        htop
        vim
        nano
    )

    log_info "Installing ${#PACKAGES[@]} packages..."

    for package in "${PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log_info "  ✓ $package (already installed)"
        else
            log_info "  → Installing $package..."
            DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$package"
            log_success "  ✓ $package installed"
        fi
    done

    log_success "All dependencies installed"
}

# Create Python virtual environment
create_venv() {
    log_step "Creating Python virtual environment..."

    cd "$INSTALL_DIR"

    if [ -d "venv" ]; then
        log_warn "Virtual environment already exists, skipping..."
    else
        su - "$PI_USER" -c "cd '$INSTALL_DIR' && python3 -m venv venv"
        log_success "Virtual environment created"
    fi
}

# Install Python packages
install_python_packages() {
    log_step "Installing Python packages..."

    cd "$INSTALL_DIR"

    # Activate venv and install packages
    su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && pip install --upgrade pip setuptools wheel"
    su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && pip install -r requirements.txt"

    log_success "Python packages installed"
}

# Install Playwright browsers
install_playwright() {
    log_step "Installing Playwright browsers..."

    cd "$INSTALL_DIR"

    # Install Playwright browser
    su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && playwright install chromium"
    su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && playwright install-deps"

    log_success "Playwright installed"
}

# Configure user groups
configure_user_groups() {
    log_step "Configuring user groups..."

    # Add user to required groups
    usermod -a -G gpio "$PI_USER" 2>/dev/null || log_warn "gpio group not available"
    usermod -a -G video "$PI_USER"
    usermod -a -G audio "$PI_USER"
    usermod -a -G pulse-access "$PI_USER" 2>/dev/null || true

    log_success "User groups configured"
}

# Create .env file
create_env_file() {
    log_step "Creating configuration file..."

    cd "$INSTALL_DIR"

    if [ -f ".env" ]; then
        log_warn ".env file already exists"
        read -p "Overwrite? (y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing .env file"
            return
        fi
    fi

    # Copy example file
    cp .env.example .env
    chown "$PI_USER:$PI_USER" .env
    chmod 600 .env

    log_success ".env file created"
    log_info ""
    log_info "╔════════════════════════════════════════════════════════════╗"
    log_info "║  IMPORTANT: Configure .env file                           ║"
    log_info "╚════════════════════════════════════════════════════════════╝"
    log_info ""
    log_info "Edit /home/$PI_USER/RaspberryMeet/.env and set:"
    log_info "  1. BBB_DEFAULT_ROOM_URL - Your BigBlueButton room URL"
    log_info "  2. BBB_DEFAULT_ROOM_PASSWORD - Room password (if required)"
    log_info "  3. WEB_PASSWORD - Web interface password (use hash_password.py)"
    log_info "  4. CALDAV_* - Calendar integration (optional)"
    log_info ""
}

# Install systemd services
install_services() {
    log_step "Installing systemd services..."

    cd "$INSTALL_DIR"

    # Copy service files
    SERVICES=(
        "raspberrymeet.service"
        "raspberrymeet-web.service"
    )

    if [ "$INSTALL_KIOSK" == "yes" ]; then
        SERVICES+=("raspberrymeet-kiosk.service")
    fi

    for service in "${SERVICES[@]}"; do
        log_info "Installing $service..."

        # Update paths in service file
        sed "s|/home/pi/RaspberryMeet|$INSTALL_DIR|g" "systemd/$service" > "/etc/systemd/system/$service"
        sed -i "s|User=pi|User=$PI_USER|g" "/etc/systemd/system/$service"
        sed -i "s|Group=pi|Group=$PI_USER|g" "/etc/systemd/system/$service"
        sed -i "s|/home/pi|$PI_HOME|g" "/etc/systemd/system/$service"

        log_success "$service installed"
    done

    # Reload systemd
    systemctl daemon-reload

    log_success "Systemd services installed"
}

# Enable systemd services
enable_services() {
    log_step "Enabling systemd services..."

    # Enable services
    systemctl enable raspberrymeet.service
    systemctl enable raspberrymeet-web.service

    if [ "$INSTALL_KIOSK" == "yes" ]; then
        systemctl enable raspberrymeet-kiosk.service
    fi

    log_success "Services enabled for autostart"
}

# Run display setup
setup_display() {
    log_step "Setting up display and kiosk mode..."

    cd "$INSTALL_DIR"

    if [ "$INSTALL_DISPLAY" != "yes" ]; then
        log_info "Skipping display setup (INSTALL_DISPLAY=no)"
        return
    fi

    # Run display setup script (non-interactive)
    export DEBIAN_FRONTEND=noninteractive
    bash scripts/setup_display.sh <<EOF
y
n
EOF

    log_success "Display setup complete"
}

# Run post-install tests
run_tests() {
    log_step "Running post-install tests..."

    cd "$INSTALL_DIR"

    # Test Python import
    if su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && python -c 'import src.utils.config'"; then
        log_success "Python modules OK"
    else
        log_error "Python module import failed"
        return 1
    fi

    # Test Playwright
    if su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && python -c 'from playwright.sync_api import sync_playwright'"; then
        log_success "Playwright OK"
    else
        log_warn "Playwright import failed (may work after reboot)"
    fi

    # Check services
    if systemctl is-enabled raspberrymeet.service &>/dev/null; then
        log_success "Systemd services OK"
    else
        log_error "Systemd services not enabled"
        return 1
    fi

    log_success "Post-install tests passed"
}

# Print post-install instructions
print_instructions() {
    echo ""
    echo "========================================================================"
    echo "  ✅ Installation Complete!"
    echo "========================================================================"
    echo ""
    echo "Next Steps:"
    echo ""
    echo "  1. Configure .env file:"
    echo "     sudo nano $INSTALL_DIR/.env"
    echo ""
    echo "  2. Set BigBlueButton room URL:"
    echo "     BBB_DEFAULT_ROOM_URL=https://your-bbb-server.com/b/room-name"
    echo ""
    echo "  3. Generate password hash (optional):"
    echo "     cd $INSTALL_DIR"
    echo "     source venv/bin/activate"
    echo "     python scripts/hash_password.py"
    echo ""
    echo "  4. Test configuration:"
    echo "     sudo systemctl start raspberrymeet"
    echo "     sudo systemctl status raspberrymeet"
    echo ""
    echo "  5. Access web interface:"
    echo "     http://$(hostname).local:8080"
    echo "     or http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
    echo "  6. Test GPIO (if wired):"
    echo "     cd $INSTALL_DIR"
    echo "     source venv/bin/activate"
    echo "     python scripts/test_gpio.py"
    echo ""
    echo "  7. Test audio/video:"
    echo "     cd $INSTALL_DIR"
    echo "     source venv/bin/activate"
    echo "     python scripts/test_audio_video.py"
    echo ""
    echo "  8. Test calendar sync (if configured):"
    echo "     cd $INSTALL_DIR"
    echo "     source venv/bin/activate"
    echo "     python scripts/test_calendar.py"
    echo ""

    if [ "$INSTALL_KIOSK" == "yes" ]; then
        echo "  📺 Kiosk Mode:"
        echo "     After reboot, system will auto-login and start in fullscreen mode"
        echo ""
    fi

    echo "Documentation:"
    echo "  • README.md - Project overview"
    echo "  • GPIO_SETUP.md - Hardware wiring"
    echo "  • AUDIO_VIDEO_SETUP.md - Audio configuration"
    echo "  • CALDAV_SETUP.md - Calendar integration"
    echo "  • KIOSK_SETUP.md - Display setup"
    echo "  • AUTOSTART.md - Service management"
    echo ""
    echo "Troubleshooting:"
    echo "  • View logs: journalctl -u raspberrymeet -f"
    echo "  • Check status: sudo systemctl status raspberrymeet"
    echo "  • Restart service: sudo systemctl restart raspberrymeet"
    echo ""
    echo "========================================================================"
    echo ""
}

# Prompt for reboot
prompt_reboot() {
    if [ "$AUTO_REBOOT" == "yes" ]; then
        log_info "AUTO_REBOOT=yes, rebooting in 5 seconds..."
        sleep 5
        reboot
        return
    fi

    echo ""
    read -p "Reboot now to complete installation? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rebooting in 5 seconds..."
        sleep 5
        reboot
    else
        log_info "Remember to reboot later: sudo reboot"
    fi
}

# Main installation flow
main() {
    print_header

    # Pre-flight checks
    check_root
    check_raspberry_pi
    check_disk_space

    echo ""
    log_info "Installation will proceed with:"
    log_info "  Install directory: $INSTALL_DIR"
    log_info "  User: $PI_USER"
    log_info "  Display setup: $INSTALL_DISPLAY"
    log_info "  Kiosk mode: $INSTALL_KIOSK"
    log_info "  Services: $INSTALL_SERVICES"
    echo ""

    read -p "Continue with installation? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled"
        exit 0
    fi

    echo ""
    log_info "Starting installation..."
    echo ""

    # Installation steps
    update_system
    install_dependencies
    create_venv
    install_python_packages
    install_playwright
    configure_user_groups
    create_env_file

    if [ "$INSTALL_SERVICES" == "yes" ]; then
        install_services
        enable_services
    fi

    if [ "$INSTALL_DISPLAY" == "yes" ]; then
        setup_display
    fi

    # Post-install
    run_tests
    print_instructions
    prompt_reboot
}

# Run main function
main "$@"
