#!/bin/bash
#
# RaspberryMeet Display Setup
# Configures X11 for kiosk mode on Raspberry Pi
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PI_USER="${SUDO_USER:-pi}"
PI_HOME="/home/${PI_USER}"

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Install required packages
install_packages() {
    log_info "Installing required packages..."

    apt-get update -qq

    # X11 and display manager packages
    PACKAGES=(
        xserver-xorg           # X11 server
        x11-xserver-utils      # X11 utilities (xset, xrandr, etc.)
        xinit                  # startx command
        openbox                # Lightweight window manager
        chromium-browser       # Web browser
        unclutter              # Hide mouse cursor
        xdotool                # X11 automation tool
        lightdm                # Display manager for auto-login
    )

    for package in "${PACKAGES[@]}"; do
        if dpkg -l | grep -q "^ii  $package "; then
            log_info "$package already installed"
        else
            log_info "Installing $package..."
            apt-get install -y "$package" > /dev/null 2>&1
            log_success "$package installed"
        fi
    done

    log_success "All packages installed"
}

# Configure auto-login
configure_autologin() {
    log_info "Configuring auto-login for user '$PI_USER'..."

    # Create LightDM configuration directory
    mkdir -p /etc/lightdm/lightdm.conf.d

    # Create auto-login configuration
    cat > /etc/lightdm/lightdm.conf.d/50-raspberrymeet.conf <<EOF
# RaspberryMeet Auto-Login Configuration
[Seat:*]
autologin-user=${PI_USER}
autologin-user-timeout=0
user-session=openbox
EOF

    log_success "Auto-login configured for user '$PI_USER'"
}

# Create .xinitrc for kiosk session
create_xinitrc() {
    log_info "Creating .xinitrc for kiosk session..."

    cat > "${PI_HOME}/.xinitrc" <<'EOF'
#!/bin/bash
#
# RaspberryMeet X11 Startup Script
# Automatically launched when X11 session starts
#

# Disable screen blanking and power management
xset -dpms
xset s off
xset s noblank

# Start window manager
openbox &

# Wait for window manager to start
sleep 2

# Start RaspberryMeet kiosk browser
/home/pi/RaspberryMeet/scripts/launch_kiosk_browser.sh
EOF

    chmod +x "${PI_HOME}/.xinitrc"
    chown ${PI_USER}:${PI_USER} "${PI_HOME}/.xinitrc"

    log_success ".xinitrc created"
}

# Create Openbox configuration
create_openbox_config() {
    log_info "Creating Openbox configuration..."

    mkdir -p "${PI_HOME}/.config/openbox"

    # Openbox autostart
    cat > "${PI_HOME}/.config/openbox/autostart" <<'EOF'
# RaspberryMeet Openbox Autostart

# Disable screen blanking
xset -dpms &
xset s off &
xset s noblank &

# Hide mouse cursor after 5 seconds
unclutter -idle 5 -root &
EOF

    # Openbox config (minimal, no decorations)
    cat > "${PI_HOME}/.config/openbox/rc.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <applications>
    <!-- Chromium fullscreen, no decorations -->
    <application class="Chromium-browser">
      <decor>no</decor>
      <maximized>true</maximized>
      <fullscreen>yes</fullscreen>
    </application>
    <application class="Chromium">
      <decor>no</decor>
      <maximized>true</maximized>
      <fullscreen>yes</fullscreen>
    </application>
  </applications>
  <keyboard>
    <!-- Disable Alt+Tab window switching -->
    <chainQuitKey>C-g</chainQuitKey>
  </keyboard>
  <mouse>
    <dragThreshold>8</dragThreshold>
  </mouse>
</openbox_config>
EOF

    chmod +x "${PI_HOME}/.config/openbox/autostart"
    chown -R ${PI_USER}:${PI_USER} "${PI_HOME}/.config/openbox"

    log_success "Openbox configuration created"
}

# Disable sleep and screen blanking in systemd
disable_system_sleep() {
    log_info "Disabling system sleep and screen blanking..."

    # Disable sleep targets
    systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

    log_success "System sleep disabled"
}

# Configure HDMI output
configure_hdmi() {
    log_info "Configuring HDMI output..."

    # Raspberry Pi config
    CONFIG_FILE="/boot/config.txt"
    if [ ! -f "$CONFIG_FILE" ]; then
        CONFIG_FILE="/boot/firmware/config.txt"
    fi

    if [ -f "$CONFIG_FILE" ]; then
        # Backup original config
        cp "$CONFIG_FILE" "${CONFIG_FILE}.bak.$(date +%Y%m%d)"

        # Ensure HDMI is forced on
        if ! grep -q "^hdmi_force_hotplug=1" "$CONFIG_FILE"; then
            echo "" >> "$CONFIG_FILE"
            echo "# RaspberryMeet HDMI Configuration" >> "$CONFIG_FILE"
            echo "hdmi_force_hotplug=1" >> "$CONFIG_FILE"
            echo "hdmi_drive=2" >> "$CONFIG_FILE"
            log_success "HDMI forced on in config.txt"
        else
            log_info "HDMI already configured in config.txt"
        fi
    else
        log_warn "config.txt not found - skipping HDMI configuration"
    fi
}

# Create startup test script
create_test_script() {
    log_info "Creating display test script..."

    cat > "${PI_HOME}/test_display.sh" <<'EOF'
#!/bin/bash
#
# Test X11 display and kiosk mode
#

echo "Testing X11 display..."
echo "DISPLAY=$DISPLAY"

# Test X server
if xset q &>/dev/null; then
    echo "✅ X11 server is running"
else
    echo "❌ X11 server is NOT running"
    echo "Start with: startx"
    exit 1
fi

# Check screen resolution
RESOLUTION=$(xdpyinfo | grep dimensions | awk '{print $2}')
echo "✅ Screen resolution: $RESOLUTION"

# Check for window manager
if pgrep -x openbox > /dev/null; then
    echo "✅ Openbox window manager is running"
else
    echo "⚠️  Openbox is not running"
fi

# Check for Chromium
if pgrep -f chromium > /dev/null; then
    echo "✅ Chromium browser is running"
else
    echo "ℹ️  Chromium is not running"
fi

echo ""
echo "Display setup is working correctly!"
EOF

    chmod +x "${PI_HOME}/test_display.sh"
    chown ${PI_USER}:${PI_USER} "${PI_HOME}/test_display.sh"

    log_success "Test script created: ${PI_HOME}/test_display.sh"
}

# Show summary
show_summary() {
    echo ""
    echo "========================================================================"
    echo "  Display Setup Complete!"
    echo "========================================================================"
    echo ""
    echo "Configuration Summary:"
    echo "  - Auto-login user: $PI_USER"
    echo "  - Display manager: LightDM"
    echo "  - Window manager: Openbox"
    echo "  - Browser: Chromium (kiosk mode)"
    echo "  - Screen blanking: Disabled"
    echo "  - System sleep: Disabled"
    echo ""
    echo "Next Steps:"
    echo "  1. Reboot the system: sudo reboot"
    echo "  2. After reboot, X11 will start automatically"
    echo "  3. Chromium will launch in kiosk mode"
    echo "  4. RaspberryMeet will control the browser"
    echo ""
    echo "Testing:"
    echo "  - Test display: ${PI_HOME}/test_display.sh"
    echo "  - Manual browser launch: ${PI_HOME}/RaspberryMeet/scripts/launch_kiosk_browser.sh"
    echo ""
    echo "Troubleshooting:"
    echo "  - View X11 logs: cat ~/.local/share/xorg/Xorg.0.log"
    echo "  - View LightDM logs: journalctl -u lightdm"
    echo "  - Manual X11 start: startx"
    echo ""
    echo "========================================================================"
    echo ""
}

# Main installation
main() {
    echo ""
    echo "========================================================================"
    echo "  RaspberryMeet Display Setup"
    echo "========================================================================"
    echo ""

    check_root

    log_info "This script will configure X11 for kiosk mode"
    log_info "User: $PI_USER"
    echo ""

    read -p "Continue with installation? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled"
        exit 0
    fi

    echo ""

    install_packages
    configure_autologin
    create_xinitrc
    create_openbox_config
    disable_system_sleep
    configure_hdmi
    create_test_script

    show_summary

    read -p "Reboot now? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rebooting in 5 seconds..."
        sleep 5
        reboot
    else
        log_info "Remember to reboot later: sudo reboot"
    fi
}

# Run main function
main
