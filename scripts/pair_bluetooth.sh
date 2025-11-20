#!/bin/bash
# RaspberryMeet - Bluetooth Pairing Script
# Helps pair Bluetooth conference speakerphones

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if Bluetooth is available
check_bluetooth() {
    if ! command -v bluetoothctl &> /dev/null; then
        print_error "Bluetooth not available"
        print_info "Installing Bluetooth packages..."
        sudo apt update
        sudo apt install -y bluez bluez-tools pulseaudio-module-bluetooth
        print_success "Bluetooth packages installed"
    fi

    # Check if bluetooth service is running
    if ! systemctl is-active --quiet bluetooth; then
        print_warning "Bluetooth service not running"
        print_info "Starting Bluetooth service..."
        sudo systemctl start bluetooth
        sudo systemctl enable bluetooth
    fi

    print_success "Bluetooth is available"
}

# Power on Bluetooth
power_on_bluetooth() {
    print_info "Powering on Bluetooth adapter..."

    bluetoothctl <<EOF
power on
agent on
default-agent
EOF

    sleep 2
    print_success "Bluetooth adapter powered on"
}

# Scan for devices
scan_devices() {
    print_header "Scanning for Bluetooth Devices"

    print_info "Scanning for 15 seconds..."
    print_info "Make sure your speakerphone is in pairing mode!"
    echo ""

    # Start scanning in background
    bluetoothctl scan on &
    SCAN_PID=$!

    sleep 15

    # Stop scanning
    kill $SCAN_PID 2>/dev/null || true

    echo ""
    print_success "Scan complete"
}

# List available devices
list_devices() {
    print_header "Available Bluetooth Devices"

    devices=$(bluetoothctl devices)

    if [ -z "$devices" ]; then
        print_warning "No devices found"
        return 1
    fi

    echo "$devices"
    echo ""

    return 0
}

# Pair with device
pair_device() {
    local mac_address="$1"

    print_info "Pairing with device: $mac_address"

    # Trust and pair
    bluetoothctl <<EOF
trust $mac_address
pair $mac_address
connect $mac_address
EOF

    sleep 3

    # Check if paired
    if bluetoothctl info "$mac_address" | grep -q "Paired: yes"; then
        print_success "Successfully paired with $mac_address"

        # Set as audio device
        print_info "Configuring as audio device..."
        pactl load-module module-bluetooth-discover 2>/dev/null || true

        return 0
    else
        print_error "Failed to pair with $mac_address"
        return 1
    fi
}

# Show paired devices
show_paired() {
    print_header "Paired Devices"

    paired_devices=$(bluetoothctl paired-devices)

    if [ -z "$paired_devices" ]; then
        print_info "No paired devices"
        return
    fi

    echo "$paired_devices"
    echo ""

    # Show connection status
    while IFS= read -r line; do
        mac=$(echo "$line" | awk '{print $2}')
        if bluetoothctl info "$mac" | grep -q "Connected: yes"; then
            name=$(echo "$line" | cut -d' ' -f3-)
            print_success "$name is connected"
        fi
    done <<< "$paired_devices"
}

# Connect to paired device
connect_device() {
    local mac_address="$1"

    print_info "Connecting to $mac_address..."

    if bluetoothctl connect "$mac_address"; then
        print_success "Connected to $mac_address"

        # Wait for audio card to appear
        sleep 3

        # Reload PulseAudio modules
        pactl load-module module-bluetooth-discover 2>/dev/null || true

        return 0
    else
        print_error "Failed to connect to $mac_address"
        return 1
    fi
}

# Disconnect device
disconnect_device() {
    local mac_address="$1"

    print_info "Disconnecting from $mac_address..."

    if bluetoothctl disconnect "$mac_address"; then
        print_success "Disconnected from $mac_address"
        return 0
    else
        print_error "Failed to disconnect from $mac_address"
        return 1
    fi
}

# Remove paired device
remove_device() {
    local mac_address="$1"

    print_warning "Removing device $mac_address..."

    if bluetoothctl remove "$mac_address"; then
        print_success "Removed $mac_address"
        return 0
    else
        print_error "Failed to remove $mac_address"
        return 1
    fi
}

# Auto-pair wizard
auto_pair_wizard() {
    print_header "Bluetooth Pairing Wizard"

    echo "This wizard will help you pair your Bluetooth speakerphone."
    echo ""
    print_warning "Before continuing:"
    echo "  1. Turn on your Bluetooth speakerphone"
    echo "  2. Put it in pairing mode (usually a Bluetooth button)"
    echo "  3. Keep it close to the Raspberry Pi"
    echo ""
    read -p "Press Enter when ready..."

    # Scan for devices
    scan_devices

    # List found devices
    if ! list_devices; then
        print_error "No devices found. Please try again."
        return 1
    fi

    # Ask user to select device
    echo "Enter the MAC address of your device (e.g., 00:11:22:33:44:55):"
    read -p "MAC Address: " mac_address

    if [ -z "$mac_address" ]; then
        print_error "No MAC address provided"
        return 1
    fi

    # Pair with device
    if pair_device "$mac_address"; then
        print_header "Pairing Successful"
        print_success "Your speakerphone is now paired!"
        echo ""
        print_info "Next steps:"
        echo "  1. Check audio devices: pactl list sinks short"
        echo "  2. Set as default: run setup_audio.sh"
        echo "  3. Test audio: speaker-test -t wav -c 2"
        return 0
    else
        print_error "Pairing failed. Please try again."
        return 1
    fi
}

# Main menu
main() {
    print_header "RaspberryMeet Bluetooth Pairing"

    # Check requirements
    check_bluetooth
    power_on_bluetooth

    while true; do
        echo ""
        echo "Bluetooth Pairing Options:"
        echo "  1) Auto-pair wizard (recommended)"
        echo "  2) Scan for devices"
        echo "  3) Show paired devices"
        echo "  4) Connect to paired device"
        echo "  5) Disconnect device"
        echo "  6) Remove paired device"
        echo "  7) Exit"
        echo ""
        read -p "Enter your choice (1-7): " choice

        case $choice in
            1)
                auto_pair_wizard
                ;;
            2)
                scan_devices
                list_devices
                ;;
            3)
                show_paired
                ;;
            4)
                show_paired
                echo ""
                read -p "Enter MAC address to connect: " mac
                connect_device "$mac"
                ;;
            5)
                show_paired
                echo ""
                read -p "Enter MAC address to disconnect: " mac
                disconnect_device "$mac"
                ;;
            6)
                show_paired
                echo ""
                read -p "Enter MAC address to remove: " mac
                read -p "Are you sure? (y/n): " confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    remove_device "$mac"
                fi
                ;;
            7)
                print_header "Pairing Complete"
                echo ""
                print_success "Bluetooth pairing finished"
                echo ""
                print_info "Your Bluetooth devices are ready to use"
                echo "Run setup_audio.sh to configure them as default audio devices"
                echo ""
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
    done
}

# Run main
main
