# RaspberryMeet Installation Guide

Complete installation instructions for RaspberryMeet on Raspberry Pi.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Manual Installation](#manual-installation)
4. [Configuration](#configuration)
5. [First Run](#first-run)
6. [Updates](#updates)
7. [Troubleshooting](#troubleshooting)
8. [Uninstallation](#uninstallation)

---

## Prerequisites

### Hardware Requirements

**Minimum:**
- Raspberry Pi 3B+ or newer
- 16GB microSD card (Class 10 or better)
- 2GB RAM
- Power supply (5V 2.5A minimum)
- HDMI display
- Network connection (Ethernet or WiFi)

**Recommended:**
- Raspberry Pi 4 (4GB or 8GB RAM)
- 32GB+ microSD card (UHS-I)
- 5V 3A power supply
- Ethernet connection (more stable than WiFi)
- USB conference speakerphone (Jabra, Anker, eMeet)
- USB webcam (1080p)

**Optional:**
- GPIO buttons and LEDs
- Touch screen display
- Bluetooth speakerphone

### Software Requirements

**Operating System:**
- Raspberry Pi OS (Debian 11 Bullseye or newer)
- Raspberry Pi OS Lite (recommended for headless)
- 64-bit version recommended for Pi 4

**Fresh Install Recommended:**
Use Raspberry Pi Imager to flash a clean OS image.

### Network Requirements

- Internet connection for installation
- Access to BigBlueButton server
- (Optional) Access to Nextcloud/CalDAV server

---

## Quick Installation

### One-Command Setup

```bash
# 1. Clone repository
cd /home/pi
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet

# 2. Run installation script
sudo ./scripts/install.sh
```

The installation script will:
1. ✅ Update system packages
2. ✅ Install all dependencies
3. ✅ Create Python virtual environment
4. ✅ Install Python packages
5. ✅ Install Playwright browser
6. ✅ Configure user permissions
7. ✅ Set up display and kiosk mode
8. ✅ Install systemd services
9. ✅ Create configuration file

**Time:** 15-30 minutes (depending on network speed)

### Post-Installation

1. **Configure .env file:**
   ```bash
   sudo nano /home/pi/RaspberryMeet/.env
   ```

2. **Set minimum required values:**
   ```bash
   BBB_DEFAULT_ROOM_URL=https://your-bbb-server.com/b/room-name
   BBB_DEFAULT_ROOM_PASSWORD=your-room-password
   WEB_PASSWORD=sha256:your-hashed-password
   ```

3. **Reboot:**
   ```bash
   sudo reboot
   ```

4. **Access web interface:**
   ```
   http://raspberrypi.local:8080
   ```

---

## Manual Installation

### Step 1: System Update

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 2: Install Dependencies

```bash
sudo apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    build-essential git curl wget \
    pulseaudio pulseaudio-utils alsa-utils v4l-utils \
    bluez bluez-tools \
    xserver-xorg x11-xserver-utils xinit openbox lightdm \
    unclutter xdotool chromium-browser \
    htop vim nano
```

### Step 3: Clone Repository

```bash
cd /home/pi
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Python Packages

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 6: Install Playwright

```bash
playwright install chromium
playwright install-deps
```

### Step 7: Configure User Permissions

```bash
sudo usermod -a -G gpio pi
sudo usermod -a -G video pi
sudo usermod -a -G audio pi
sudo usermod -a -G pulse-access pi
```

**Logout and login for group changes to take effect.**

### Step 8: Display Setup (Kiosk Mode)

```bash
sudo ./scripts/setup_display.sh
```

Follow prompts to configure auto-login and kiosk mode.

### Step 9: Install Systemd Services

```bash
sudo ./scripts/install_services.sh
```

Select services to install:
- `[1]` raspberrymeet.service - Main orchestrator
- `[2]` raspberrymeet-web.service - Web interface
- `[3]` raspberrymeet-kiosk.service - Kiosk browser

### Step 10: Create Configuration

```bash
cp .env.example .env
nano .env
```

Fill in required values (see [Configuration](#configuration) section).

### Step 11: Enable Services

```bash
sudo systemctl enable raspberrymeet
sudo systemctl enable raspberrymeet-web
sudo systemctl enable raspberrymeet-kiosk
```

### Step 12: Reboot

```bash
sudo reboot
```

---

## Configuration

### Required Configuration

Edit `/home/pi/RaspberryMeet/.env`:

```bash
# BigBlueButton
BBB_DEFAULT_ROOM_URL=https://bbb.example.com/b/room-abc-def
BBB_DEFAULT_ROOM_PASSWORD=secure-room-password
BBB_DEFAULT_USERNAME=Meeting Room 1

# Web Interface
WEB_USERNAME=admin
WEB_PASSWORD=sha256:your-hash-here
```

### Generate Password Hash

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/hash_password.py
```

Enter your desired password and copy the generated hash to `WEB_PASSWORD`.

### Optional Configuration

**CalDAV Calendar Integration:**
```bash
CALDAV_ENABLED=true
CALDAV_URL=https://nextcloud.example.com/remote.php/dav
CALDAV_USERNAME=meeting-room-1@example.com
CALDAV_PASSWORD=app-password-here
CALDAV_CALENDAR_NAME=Meetings
```

**GPIO Pins:**
```bash
GPIO_ENABLED=true
GPIO_JOIN_BUTTON_PIN=17
GPIO_STATUS_LED_GREEN_PIN=23
GPIO_STATUS_LED_RED_PIN=24
```

**Audio Preferences:**
```bash
AUDIO_PREFERRED_DEVICE=Jabra Speak 510
```

---

## First Run

### Start Services

```bash
sudo systemctl start raspberrymeet
sudo systemctl start raspberrymeet-web
sudo systemctl start raspberrymeet-kiosk
```

### Check Status

```bash
sudo systemctl status raspberrymeet
```

Expected output:
```
● raspberrymeet.service - RaspberryMeet Meeting Orchestrator
   Loaded: loaded
   Active: active (running)
```

### View Logs

```bash
journalctl -u raspberrymeet -f
```

### Access Web Interface

Open browser to:
```
http://raspberrypi.local:8080
```

Or use IP address:
```
http://192.168.1.X:8080
```

**Login:**
- Username: `admin` (or your WEB_USERNAME)
- Password: (your unhashed password)

### Test GPIO (If Wired)

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/test_gpio.py
```

### Test Audio/Video

```bash
python scripts/test_audio_video.py
```

### Test Calendar Sync

```bash
python scripts/test_calendar.py
```

---

## Updates

### Update to Latest Version

```bash
cd /home/pi/RaspberryMeet
sudo ./scripts/update.sh
```

This will:
1. Stop services
2. Backup `.env` file
3. Pull latest changes from Git
4. Update Python packages
5. Update Playwright
6. Update systemd services
7. Restart services

### Update to Specific Branch

```bash
sudo ./scripts/update.sh develop
```

### Manual Update

```bash
cd /home/pi/RaspberryMeet
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
playwright install chromium
sudo systemctl restart raspberrymeet
```

---

## Troubleshooting

### Installation Fails

**Problem:** `apt-get install` fails with dependency errors

**Solution:**
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -f
```

---

**Problem:** Insufficient disk space

**Solution:**
```bash
# Check space
df -h

# Clean package cache
sudo apt-get clean
sudo apt-get autoremove

# Remove old kernels
sudo apt-get remove --purge $(dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d')
```

---

**Problem:** Python package installation fails

**Solution:**
```bash
# Install build dependencies
sudo apt-get install -y python3-dev build-essential libssl-dev libffi-dev

# Upgrade pip
python -m pip install --upgrade pip

# Install packages with verbose output
pip install -r requirements.txt -v
```

---

### Services Not Starting

**Problem:** `systemctl start raspberrymeet` fails

**Solution:**
```bash
# Check service status
sudo systemctl status raspberrymeet

# View full logs
journalctl -u raspberrymeet -n 50

# Check for Python errors
sudo -u pi bash -c "cd /home/pi/RaspberryMeet && source venv/bin/activate && python -m src.orchestrator.main"
```

---

**Problem:** `.env` file not found

**Solution:**
```bash
cd /home/pi/RaspberryMeet
cp .env.example .env
sudo nano .env
# Fill in required values
sudo systemctl restart raspberrymeet
```

---

### Web Interface Not Accessible

**Problem:** Cannot access `http://raspberrypi.local:8080`

**Solution:**
```bash
# Check if web service is running
sudo systemctl status raspberrymeet-web

# Check port binding
sudo netstat -tulpn | grep 8080

# Try IP address instead
hostname -I
# Access http://<IP>:8080

# Check firewall
sudo ufw status
sudo ufw allow 8080/tcp
```

---

### Kiosk Mode Not Starting

**Problem:** No GUI after reboot

**Solution:**
```bash
# Check X11 logs
cat ~/.local/share/xorg/Xorg.0.log

# Check LightDM
sudo systemctl status lightdm

# Start X11 manually
startx

# Reconfigure display
sudo ./scripts/setup_display.sh
```

---

### GPIO Not Working

**Problem:** GPIO test script fails

**Solution:**
```bash
# Check if user in gpio group
groups pi

# Add user to gpio group
sudo usermod -a -G gpio pi

# Logout and login

# Check GPIO access
ls -la /dev/gpiomem

# Install RPi.GPIO
source venv/bin/activate
pip install RPi.GPIO
```

---

### Audio Issues

**Problem:** No audio output or microphone not detected

**Solution:**
```bash
# Check PulseAudio
pactl info

# List audio devices
pactl list sinks
pactl list sources

# Run audio setup
./scripts/setup_audio.sh

# Test audio
speaker-test -c 2 -r 48000

# Restart PulseAudio
pulseaudio -k
pulseaudio --start
```

---

### Calendar Sync Fails

**Problem:** CalDAV connection errors

**Solution:**
```bash
# Test CalDAV connection manually
curl -u username:password https://nextcloud.example.com/remote.php/dav

# Check .env configuration
grep CALDAV /home/pi/RaspberryMeet/.env

# Test with mock mode
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/test_calendar.py
```

---

## Uninstallation

### Remove RaspberryMeet

```bash
# Stop and disable services
sudo systemctl stop raspberrymeet raspberrymeet-web raspberrymeet-kiosk
sudo systemctl disable raspberrymeet raspberrymeet-web raspberrymeet-kiosk

# Remove service files
sudo rm /etc/systemd/system/raspberrymeet*.service
sudo systemctl daemon-reload

# Remove installation directory
sudo rm -rf /home/pi/RaspberryMeet

# (Optional) Remove dependencies
sudo apt-get remove --purge chromium-browser openbox lightdm
sudo apt-get autoremove
```

### Restore Display Settings

```bash
# Disable auto-login
sudo rm /etc/lightdm/lightdm.conf.d/50-raspberrymeet.conf

# Remove xinitrc
rm ~/.xinitrc

# Restore default boot target
sudo systemctl set-default multi-user.target
```

---

## Advanced Installation

### Custom Installation Directory

```bash
export INSTALL_DIR=/opt/raspberrymeet
sudo mkdir -p $INSTALL_DIR
sudo chown pi:pi $INSTALL_DIR
cd $INSTALL_DIR
git clone https://github.com/Sico93/RaspberryMeet.git .
sudo INSTALL_DIR=$INSTALL_DIR ./scripts/install.sh
```

### Headless Installation (No Kiosk)

```bash
export INSTALL_KIOSK=no
export INSTALL_DISPLAY=no
sudo ./scripts/install.sh
```

### Automated Installation (CI/CD)

```bash
export INSTALL_KIOSK=yes
export INSTALL_DISPLAY=yes
export AUTO_REBOOT=yes
sudo ./scripts/install.sh <<EOF
y
EOF
```

### Multi-Room Installation

For multiple meeting rooms on same network:

```bash
# Room 1
hostname: raspberrypi-room1
IP: 192.168.1.101
Port: 8080

# Room 2
hostname: raspberrypi-room2
IP: 192.168.1.102
Port: 8080

# Configure different BBB rooms in each .env file
```

---

## Performance Optimization

### Raspberry Pi Configuration

Edit `/boot/config.txt`:

```ini
# GPU memory
gpu_mem=256

# Overclock (Pi 4 only, requires cooling)
over_voltage=2
arm_freq=1750

# Disable unused features
dtoverlay=disable-wifi  # If using Ethernet
dtoverlay=disable-bt    # If not using Bluetooth
```

### Reduce Memory Usage

```bash
# Disable swap
sudo dphys-swapfile swapoff
sudo dphys-swapfile uninstall

# Reduce logging
sudo journalctl --vacuum-time=7d
```

### Network Optimization

```bash
# Increase network buffers
sudo sysctl -w net.core.rmem_max=2097152
sudo sysctl -w net.core.wmem_max=2097152

# Make persistent
echo "net.core.rmem_max=2097152" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max=2097152" | sudo tee -a /etc/sysctl.conf
```

---

## Security Hardening

### SSH Configuration

```bash
# Change default SSH port
sudo nano /etc/ssh/sshd_config
# Port 2222

# Disable root login
# PermitRootLogin no

# Restart SSH
sudo systemctl restart ssh
```

### Firewall Setup

```bash
# Install UFW
sudo apt-get install ufw

# Allow SSH and web interface
sudo ufw allow 22/tcp
sudo ufw allow 8080/tcp

# Enable firewall
sudo ufw enable
```

### User Passwords

```bash
# Change pi user password
passwd

# Generate strong web password
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/hash_password.py
```

---

## Backup and Recovery

### Backup Configuration

```bash
# Backup .env file
cp /home/pi/RaspberryMeet/.env ~/raspberrymeet-backup.env

# Backup to USB drive
sudo mount /dev/sda1 /mnt
sudo cp -r /home/pi/RaspberryMeet /mnt/raspberrymeet-backup
sudo umount /mnt
```

### Create SD Card Image

```bash
# On Linux host
sudo dd if=/dev/sdX of=raspberrymeet-backup.img bs=4M status=progress

# Compress
gzip raspberrymeet-backup.img
```

### Restore from Backup

```bash
# Restore .env
cp ~/raspberrymeet-backup.env /home/pi/RaspberryMeet/.env

# Restart services
sudo systemctl restart raspberrymeet
```

---

## Support and Documentation

- **README.md** - Project overview
- **GPIO_SETUP.md** - Hardware wiring guide
- **AUDIO_VIDEO_SETUP.md** - Audio configuration
- **CALDAV_SETUP.md** - Calendar integration
- **KIOSK_SETUP.md** - Display and kiosk mode
- **AUTOSTART.md** - Service management
- **TROUBLESHOOTING.md** - Common issues

**GitHub Issues:** https://github.com/Sico93/RaspberryMeet/issues

---

**Last Updated:** 2025-11-19
**RaspberryMeet Version:** 1.0.0
