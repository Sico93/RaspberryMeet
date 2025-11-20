#!/bin/bash
# RaspberryMeet - Audio Setup Script
# Configures PulseAudio for conference speakerphone usage

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

# Check if PulseAudio is installed
check_pulseaudio() {
    if ! command -v pulseaudio &> /dev/null; then
        print_error "PulseAudio not installed"
        print_info "Installing PulseAudio..."
        sudo apt update
        sudo apt install -y pulseaudio pulseaudio-utils
    fi

    print_success "PulseAudio is installed"
}

# Check if v4l2 tools are installed
check_v4l2() {
    if ! command -v v4l2-ctl &> /dev/null; then
        print_warning "v4l2-utils not installed"
        print_info "Installing v4l2-utils..."
        sudo apt install -y v4l2-utils
    fi

    print_success "v4l2-utils is installed"
}

# List audio devices
list_audio_devices() {
    print_header "Audio Devices"

    echo "Input Devices (Microphones):"
    echo "───────────────────────────────"
    pactl list sources short | grep -v "monitor" || echo "  No input devices found"
    echo ""

    echo "Output Devices (Speakers):"
    echo "───────────────────────────────"
    pactl list sinks short || echo "  No output devices found"
    echo ""
}

# List video devices
list_video_devices() {
    print_header "Video Devices"

    echo "Webcams:"
    echo "───────────────────────────────"

    found_devices=false
    for dev in /dev/video*; do
        if [ -e "$dev" ]; then
            found_devices=true
            echo "  $dev:"

            # Try to get device name
            if command -v v4l2-ctl &> /dev/null; then
                name=$(v4l2-ctl --device="$dev" --info 2>/dev/null | grep "Card type" | cut -d: -f2 | xargs || echo "Unknown")
                echo "    Name: $name"
            fi
        fi
    done

    if [ "$found_devices" = false ]; then
        echo "  No video devices found"
    fi

    echo ""
}

# Set default audio devices
set_defaults() {
    print_header "Setting Default Audio Devices"

    # List current defaults
    echo "Current defaults:"
    echo "  Source: $(pactl get-default-source)"
    echo "  Sink: $(pactl get-default-sink)"
    echo ""

    # Offer to change
    read -p "Do you want to change default audio devices? (y/n): " change_default

    if [[ ! "$change_default" =~ ^[Yy]$ ]]; then
        print_info "Keeping current defaults"
        return
    fi

    # Get available sources
    echo ""
    echo "Available input devices:"
    sources=($(pactl list sources short | grep -v "monitor" | awk '{print $2}'))
    for i in "${!sources[@]}"; do
        desc=$(pactl list sources | grep -A 10 "${sources[$i]}" | grep "Description:" | cut -d: -f2 | xargs)
        echo "  $((i+1))) $desc"
    done

    if [ ${#sources[@]} -gt 0 ]; then
        echo ""
        read -p "Select input device (1-${#sources[@]}): " source_choice
        if [ "$source_choice" -ge 1 ] && [ "$source_choice" -le ${#sources[@]} ]; then
            selected_source="${sources[$((source_choice-1))]}"
            pactl set-default-source "$selected_source"
            print_success "Default input set to: $selected_source"
        fi
    fi

    # Get available sinks
    echo ""
    echo "Available output devices:"
    sinks=($(pactl list sinks short | awk '{print $2}'))
    for i in "${!sinks[@]}"; do
        desc=$(pactl list sinks | grep -A 10 "${sinks[$i]}" | grep "Description:" | cut -d: -f2 | xargs)
        echo "  $((i+1))) $desc"
    done

    if [ ${#sinks[@]} -gt 0 ]; then
        echo ""
        read -p "Select output device (1-${#sinks[@]}): " sink_choice
        if [ "$sink_choice" -ge 1 ] && [ "$sink_choice" -le ${#sinks[@]} ]; then
            selected_sink="${sinks[$((sink_choice-1))]}"
            pactl set-default-sink "$selected_sink"
            print_success "Default output set to: $selected_sink"
        fi
    fi
}

# Test audio
test_audio() {
    print_header "Audio Test"

    echo "Testing audio output (speaker)..."
    echo ""

    if command -v speaker-test &> /dev/null; then
        print_info "Playing test sound for 3 seconds..."
        print_info "You should hear white noise"
        timeout 3 speaker-test -t wav -c 2 2>/dev/null || true
        print_success "Speaker test complete"
    else
        print_warning "speaker-test not available"
        print_info "Install: sudo apt install alsa-utils"
    fi

    echo ""
    read -p "Test microphone? (y/n): " test_mic

    if [[ "$test_mic" =~ ^[Yy]$ ]]; then
        if command -v arecord &> /dev/null; then
            print_info "Recording 3 seconds from microphone..."
            arecord -d 3 -f cd /tmp/mic_test.wav 2>/dev/null

            print_info "Playing back recording..."
            aplay /tmp/mic_test.wav 2>/dev/null
            rm /tmp/mic_test.wav

            print_success "Microphone test complete"
        else
            print_warning "arecord not available"
            print_info "Install: sudo apt install alsa-utils"
        fi
    fi
}

# Configure PulseAudio for network access (optional)
configure_network_audio() {
    print_header "Network Audio (Optional)"

    echo "This allows audio streaming over the network."
    echo "Only enable if you need remote audio access."
    echo ""
    read -p "Enable network audio? (y/n): " enable_network

    if [[ ! "$enable_network" =~ ^[Yy]$ ]]; then
        return
    fi

    # Backup config
    if [ -f "/etc/pulse/default.pa" ]; then
        sudo cp /etc/pulse/default.pa /etc/pulse/default.pa.bak
        print_info "Backup created: /etc/pulse/default.pa.bak"
    fi

    # Add network modules
    if ! grep -q "load-module module-native-protocol-tcp" /etc/pulse/default.pa; then
        echo "load-module module-native-protocol-tcp auth-anonymous=1" | sudo tee -a /etc/pulse/default.pa
        print_success "Network audio enabled"
        print_warning "PulseAudio restart required: pulseaudio -k"
    else
        print_info "Network audio already enabled"
    fi
}

# Main
main() {
    print_header "RaspberryMeet Audio Setup"

    # Check requirements
    check_pulseaudio
    check_v4l2

    # Show menu
    while true; do
        echo ""
        echo "Audio/Video Setup Options:"
        echo "  1) List audio devices"
        echo "  2) List video devices"
        echo "  3) Set default audio devices"
        echo "  4) Test audio"
        echo "  5) Configure network audio (optional)"
        echo "  6) Show all information"
        echo "  7) Exit"
        echo ""
        read -p "Enter your choice (1-7): " choice

        case $choice in
            1)
                list_audio_devices
                ;;
            2)
                list_video_devices
                ;;
            3)
                set_defaults
                ;;
            4)
                test_audio
                ;;
            5)
                configure_network_audio
                ;;
            6)
                list_audio_devices
                list_video_devices
                ;;
            7)
                print_header "Setup Complete"
                echo ""
                print_success "Audio/video setup finished"
                echo ""
                echo "Current configuration:"
                echo "  Default input: $(pactl get-default-source)"
                echo "  Default output: $(pactl get-default-sink)"
                echo ""
                print_info "You can run this script again anytime to reconfigure"
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
