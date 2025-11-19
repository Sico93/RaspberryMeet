#!/bin/bash
#
# RaspberryMeet Update Script
# Updates RaspberryMeet to latest version from Git
#
# Usage: sudo ./scripts/update.sh [branch]
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
INSTALL_DIR="${INSTALL_DIR:-/home/pi/RaspberryMeet}"
PI_USER="${SUDO_USER:-pi}"
BRANCH="${1:-main}"

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

# Check root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    exit 1
fi

echo ""
echo "========================================================================"
echo "  🔄 RaspberryMeet Update"
echo "========================================================================"
echo ""
log_info "Update to branch: $BRANCH"
log_info "Install directory: $INSTALL_DIR"
echo ""

# Stop services
log_info "Stopping services..."
systemctl stop raspberrymeet-kiosk 2>/dev/null || true
systemctl stop raspberrymeet-web 2>/dev/null || true
systemctl stop raspberrymeet 2>/dev/null || true
log_success "Services stopped"

# Backup .env file
log_info "Backing up configuration..."
if [ -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env" "$INSTALL_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    log_success ".env file backed up"
fi

# Update from Git
log_info "Pulling latest changes from Git..."
cd "$INSTALL_DIR"

# Stash local changes
su - "$PI_USER" -c "cd '$INSTALL_DIR' && git stash" || true

# Fetch and pull
su - "$PI_USER" -c "cd '$INSTALL_DIR' && git fetch origin"
su - "$PI_USER" -c "cd '$INSTALL_DIR' && git checkout $BRANCH"
su - "$PI_USER" -c "cd '$INSTALL_DIR' && git pull origin $BRANCH"

log_success "Git updated to $BRANCH"

# Update Python packages
log_info "Updating Python packages..."
su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && pip install --upgrade pip"
su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && pip install -r requirements.txt --upgrade"
log_success "Python packages updated"

# Update Playwright
log_info "Updating Playwright..."
su - "$PI_USER" -c "cd '$INSTALL_DIR' && source venv/bin/activate && playwright install chromium"
log_success "Playwright updated"

# Update systemd services
log_info "Updating systemd services..."
if [ -d "$INSTALL_DIR/systemd" ]; then
    for service in "$INSTALL_DIR"/systemd/*.service; do
        service_name=$(basename "$service")
        if [ -f "/etc/systemd/system/$service_name" ]; then
            log_info "Updating $service_name..."
            sed "s|/home/pi/RaspberryMeet|$INSTALL_DIR|g" "$service" > "/etc/systemd/system/$service_name"
            sed -i "s|User=pi|User=$PI_USER|g" "/etc/systemd/system/$service_name"
            sed -i "s|Group=pi|Group=$PI_USER|g" "/etc/systemd/system/$service_name"
        fi
    done
    systemctl daemon-reload
    log_success "Systemd services updated"
fi

# Restore .env if it was overwritten
if [ -f "$INSTALL_DIR/.env.backup."* ]; then
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        LATEST_BACKUP=$(ls -t "$INSTALL_DIR"/.env.backup.* | head -1)
        cp "$LATEST_BACKUP" "$INSTALL_DIR/.env"
        log_warn ".env restored from backup"
    fi
fi

# Start services
log_info "Starting services..."
systemctl start raspberrymeet
systemctl start raspberrymeet-web
systemctl start raspberrymeet-kiosk 2>/dev/null || true
log_success "Services started"

# Show status
echo ""
log_info "Service status:"
systemctl status raspberrymeet --no-pager -l || true

echo ""
echo "========================================================================"
echo "  ✅ Update Complete!"
echo "========================================================================"
echo ""
log_info "Updated to: $(cd $INSTALL_DIR && git log -1 --oneline)"
echo ""
log_info "Check service status:"
log_info "  sudo systemctl status raspberrymeet"
log_info "  sudo systemctl status raspberrymeet-web"
log_info "  sudo systemctl status raspberrymeet-kiosk"
echo ""
log_info "View logs:"
log_info "  journalctl -u raspberrymeet -f"
echo ""
echo "========================================================================"
echo ""
