#!/bin/bash
#
# RaspberryMeet Kiosk Browser Launcher
# Starts Chromium in fullscreen kiosk mode for BigBlueButton meetings
#

set -e

# Configuration
RASPBERRYMEET_DIR="${RASPBERRYMEET_DIR:-/home/pi/RaspberryMeet}"
DISPLAY="${DISPLAY:-:0}"
CHROMIUM_USER_DATA_DIR="${HOME}/.config/chromium-kiosk"
INITIAL_URL="${KIOSK_INITIAL_URL:-about:blank}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running on Raspberry Pi
check_raspberry_pi() {
    if [ -f /proc/device-tree/model ]; then
        model=$(cat /proc/device-tree/model)
        log_info "Running on: $model"
    else
        log_warn "Not running on Raspberry Pi (or model detection failed)"
    fi
}

# Disable screen blanking and power management
disable_screen_blanking() {
    log_info "Disabling screen blanking and power management..."

    # Disable DPMS (Energy Star) features
    xset -dpms

    # Disable screen saver
    xset s off

    # Disable screen blanking
    xset s noblank

    log_info "✅ Screen blanking disabled"
}

# Hide mouse cursor after inactivity
setup_mouse_cursor() {
    log_info "Configuring mouse cursor auto-hide..."

    # Check if unclutter is installed
    if command -v unclutter &> /dev/null; then
        # Hide cursor after 5 seconds of inactivity
        unclutter -idle 5 -root &
        log_info "✅ Mouse cursor will hide after 5 seconds"
    else
        log_warn "unclutter not installed - mouse cursor will remain visible"
        log_warn "Install with: sudo apt-get install unclutter"
    fi
}

# Clean up old Chromium sessions
cleanup_chromium() {
    log_info "Cleaning up old Chromium sessions..."

    # Kill any existing Chromium processes
    pkill -f chromium-browser || true
    pkill -f chromium || true

    # Remove lock files
    rm -f "${CHROMIUM_USER_DATA_DIR}/SingletonLock" 2>/dev/null || true
    rm -f "${CHROMIUM_USER_DATA_DIR}/SingletonSocket" 2>/dev/null || true

    # Clear cache (optional, comment out to preserve cache)
    # rm -rf "${CHROMIUM_USER_DATA_DIR}/Default/Cache" 2>/dev/null || true

    log_info "✅ Cleanup complete"
}

# Set up window manager (if not already running)
setup_window_manager() {
    log_info "Checking window manager..."

    # Check if a window manager is already running
    if ! pgrep -x "openbox\|xfwm4\|mutter" > /dev/null; then
        log_info "Starting minimal window manager (openbox)..."

        if command -v openbox &> /dev/null; then
            openbox &
            sleep 2
            log_info "✅ Openbox started"
        else
            log_warn "No window manager found - Chromium will run without WM"
            log_warn "Install openbox: sudo apt-get install openbox"
        fi
    else
        log_info "✅ Window manager already running"
    fi
}

# Launch Chromium in kiosk mode
launch_chromium() {
    log_info "Launching Chromium in kiosk mode..."
    log_info "Display: $DISPLAY"
    log_info "Initial URL: $INITIAL_URL"

    # Chromium command-line flags for kiosk mode
    CHROMIUM_FLAGS=(
        # Kiosk mode
        --kiosk
        --no-first-run
        --disable-infobars
        --disable-session-crashed-bubble
        --disable-translate

        # Fullscreen
        --start-fullscreen
        --window-position=0,0

        # Privacy & Security
        --no-default-browser-check
        --disable-notifications
        --disable-popup-blocking
        --disable-background-networking
        --disable-sync
        --disable-features=TranslateUI

        # Performance
        --disable-gpu-vsync
        --disable-software-rasterizer
        --enable-gpu-rasterization
        --enable-zero-copy
        --disable-dev-shm-usage

        # Audio/Video
        --autoplay-policy=no-user-gesture-required
        --use-fake-ui-for-media-stream  # Auto-grant camera/mic permissions
        --disable-features=MediaRouter  # Disable cast

        # User data directory
        --user-data-dir="${CHROMIUM_USER_DATA_DIR}"

        # Enable WebRTC
        --enable-features=WebRTC

        # Disable restore prompts
        --disable-restore-session-state
        --disable-background-timer-throttling

        # Remote debugging (useful for development)
        --remote-debugging-port=9222
    )

    # Check if Chromium is installed
    if command -v chromium-browser &> /dev/null; then
        CHROMIUM_BIN="chromium-browser"
    elif command -v chromium &> /dev/null; then
        CHROMIUM_BIN="chromium"
    else
        log_error "Chromium not found!"
        log_error "Install with: sudo apt-get install chromium-browser"
        exit 1
    fi

    log_info "Using: $CHROMIUM_BIN"
    log_info "Starting browser..."

    # Launch Chromium
    DISPLAY=$DISPLAY $CHROMIUM_BIN "${CHROMIUM_FLAGS[@]}" "$INITIAL_URL" &

    CHROMIUM_PID=$!
    log_info "✅ Chromium started (PID: $CHROMIUM_PID)"

    # Wait for Chromium to start
    sleep 3

    # Check if still running
    if ps -p $CHROMIUM_PID > /dev/null; then
        log_info "✅ Kiosk browser is running"
    else
        log_error "Chromium failed to start or crashed immediately"
        exit 1
    fi
}

# Monitor Chromium and restart if it crashes
monitor_chromium() {
    log_info "Monitoring Chromium process..."

    while true; do
        if ! pgrep -f "chromium.*kiosk" > /dev/null; then
            log_warn "Chromium crashed! Restarting in 5 seconds..."
            sleep 5
            cleanup_chromium
            launch_chromium
        fi
        sleep 10
    done
}

# Signal handler for graceful shutdown
cleanup_on_exit() {
    log_info "Shutting down kiosk browser..."
    pkill -f chromium-browser || true
    pkill -f chromium || true
    pkill -f unclutter || true
    log_info "✅ Cleanup complete"
    exit 0
}

trap cleanup_on_exit SIGTERM SIGINT

# Main execution
main() {
    log_info "=================================================="
    log_info "  RaspberryMeet Kiosk Browser Launcher"
    log_info "=================================================="
    echo ""

    check_raspberry_pi
    disable_screen_blanking
    setup_mouse_cursor
    cleanup_chromium
    setup_window_manager
    launch_chromium

    echo ""
    log_info "=================================================="
    log_info "  Kiosk Mode Active"
    log_info "=================================================="
    log_info "Chromium is running in fullscreen kiosk mode"
    log_info "Browser is controlled by RaspberryMeet orchestrator"
    log_info "Press Ctrl+C to exit (if running manually)"
    log_info ""
    log_info "Remote debugging: http://localhost:9222"
    log_info "=================================================="
    echo ""

    # Monitor and auto-restart if crash detected
    monitor_chromium
}

# Run main function
main
