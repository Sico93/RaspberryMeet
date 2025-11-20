# Kiosk Mode Setup Guide

**RaspberryMeet** - Fullscreen BigBlueButton Meeting Room

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Automatic Setup](#automatic-setup)
4. [Manual Setup](#manual-setup)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Performance Tuning](#performance-tuning)

---

## Overview

Kiosk mode transforms your Raspberry Pi into a dedicated BigBlueButton meeting room device:

- **Fullscreen Chromium browser** - No UI distractions
- **Auto-start on boot** - No keyboard/mouse needed
- **Auto-login** - Immediate meeting room availability
- **Screen blanking disabled** - Display always on
- **Mouse cursor auto-hide** - Clean professional look
- **Crash recovery** - Auto-restart if browser crashes

### Architecture

```
Boot → LightDM (auto-login) → X11 Session → Openbox WM → Chromium Kiosk → BBB Meeting
```

---

## Quick Start

### One-Command Setup

```bash
cd /home/pi/RaspberryMeet
sudo ./scripts/setup_display.sh
```

This automatically:
1. Installs X11, Openbox, Chromium, LightDM
2. Configures auto-login
3. Sets up kiosk mode
4. Disables screen blanking
5. Creates startup scripts

**Reboot when prompted.**

After reboot, the system will:
1. Auto-login as `pi` user
2. Start X11 session
3. Launch Chromium in fullscreen kiosk mode
4. Display blank page (controlled by RaspberryMeet)

---

## Automatic Setup

### Step 1: Run Display Setup

```bash
sudo /home/pi/RaspberryMeet/scripts/setup_display.sh
```

The script will:
- Install required packages
- Configure LightDM auto-login
- Create `.xinitrc` for X11 startup
- Configure Openbox window manager
- Disable screen blanking
- Force HDMI output

**Answer prompts:**
```
Continue with installation? (y/n) y
Reboot now? (y/n) y
```

### Step 2: Enable Kiosk Service (Optional)

For systemd-managed kiosk mode:

```bash
cd /home/pi/RaspberryMeet
./scripts/install_services.sh
```

Select:
```
[3] raspberrymeet-kiosk.service - Kiosk browser
```

This makes the kiosk browser a systemd service that:
- Starts automatically on boot
- Restarts on crash
- Logs to journalctl

---

## Manual Setup

### Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y \
    xserver-xorg \
    x11-xserver-utils \
    xinit \
    openbox \
    chromium-browser \
    unclutter \
    xdotool \
    lightdm
```

### Configure Auto-Login

Create `/etc/lightdm/lightdm.conf.d/50-raspberrymeet.conf`:

```ini
[Seat:*]
autologin-user=pi
autologin-user-timeout=0
user-session=openbox
```

### Create X11 Startup Script

Create `/home/pi/.xinitrc`:

```bash
#!/bin/bash

# Disable screen blanking
xset -dpms
xset s off
xset s noblank

# Start window manager
openbox &

# Wait for WM
sleep 2

# Start kiosk browser
/home/pi/RaspberryMeet/scripts/launch_kiosk_browser.sh
```

Make executable:

```bash
chmod +x /home/pi/.xinitrc
```

### Configure Openbox

Create `/home/pi/.config/openbox/autostart`:

```bash
# Disable screen blanking
xset -dpms &
xset s off &
xset s noblank &

# Hide mouse cursor
unclutter -idle 5 -root &
```

Create `/home/pi/.config/openbox/rc.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<openbox_config xmlns="http://openbox.org/3.4/rc">
  <applications>
    <application class="Chromium-browser">
      <decor>no</decor>
      <maximized>true</maximized>
      <fullscreen>yes</fullscreen>
    </application>
  </applications>
</openbox_config>
```

### Disable System Sleep

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

### Force HDMI Output

Edit `/boot/config.txt` (or `/boot/firmware/config.txt`):

```ini
# Force HDMI output
hdmi_force_hotplug=1
hdmi_drive=2
```

### Reboot

```bash
sudo reboot
```

---

## Testing

### Test X11 Display

After reboot, X11 should start automatically. To verify:

```bash
/home/pi/test_display.sh
```

Expected output:

```
Testing X11 display...
DISPLAY=:0
✅ X11 server is running
✅ Screen resolution: 1920x1080
✅ Openbox window manager is running
✅ Chromium browser is running

Display setup is working correctly!
```

### Manual Browser Launch

If X11 is running but browser isn't:

```bash
/home/pi/RaspberryMeet/scripts/launch_kiosk_browser.sh
```

### Check Systemd Service

If using systemd kiosk service:

```bash
sudo systemctl status raspberrymeet-kiosk
```

Expected:

```
● raspberrymeet-kiosk.service - RaspberryMeet Kiosk Browser
   Loaded: loaded (/etc/systemd/system/raspberrymeet-kiosk.service)
   Active: active (running)
```

### View Logs

```bash
# Kiosk browser logs
journalctl -u raspberrymeet-kiosk -f

# X11 logs
cat ~/.local/share/xorg/Xorg.0.log

# LightDM logs
journalctl -u lightdm
```

---

## Troubleshooting

### X11 Not Starting

**Problem**: Black screen after boot, no graphical interface

**Solutions**:

1. **Check LightDM status**:
   ```bash
   sudo systemctl status lightdm
   ```

2. **Start LightDM manually**:
   ```bash
   sudo systemctl start lightdm
   ```

3. **Check X11 logs**:
   ```bash
   cat ~/.local/share/xorg/Xorg.0.log | grep EE
   ```

4. **Test X11 manually**:
   ```bash
   startx
   ```

5. **Force HDMI** (edit `/boot/config.txt`):
   ```ini
   hdmi_force_hotplug=1
   hdmi_group=2
   hdmi_mode=82  # 1920x1080 60Hz
   ```

### Chromium Not Starting

**Problem**: X11 works but Chromium doesn't launch

**Solutions**:

1. **Check Chromium installation**:
   ```bash
   which chromium-browser
   dpkg -l | grep chromium
   ```

2. **Test Chromium manually**:
   ```bash
   export DISPLAY=:0
   chromium-browser --version
   chromium-browser --kiosk http://example.com &
   ```

3. **Check for crashes**:
   ```bash
   journalctl -u raspberrymeet-kiosk | grep -i error
   ```

4. **Remove lock files**:
   ```bash
   rm -rf ~/.config/chromium-kiosk/SingletonLock
   rm -rf ~/.config/chromium-kiosk/SingletonSocket
   ```

5. **Clear Chromium cache**:
   ```bash
   rm -rf ~/.config/chromium-kiosk/Default/Cache
   ```

### Screen Blanking Still Active

**Problem**: Screen turns off after inactivity

**Solutions**:

1. **Verify xset commands**:
   ```bash
   export DISPLAY=:0
   xset q | grep -i "DPMS\|Screen Saver"
   ```

   Should show:
   ```
   DPMS is Disabled
   Screen Saver: disabled
   ```

2. **Manually disable**:
   ```bash
   export DISPLAY=:0
   xset -dpms
   xset s off
   xset s noblank
   ```

3. **Add to rc.local** (fallback):
   ```bash
   sudo nano /etc/rc.local
   ```

   Add before `exit 0`:
   ```bash
   su - pi -c "DISPLAY=:0 xset -dpms"
   su - pi -c "DISPLAY=:0 xset s off"
   su - pi -c "DISPLAY=:0 xset s noblank"
   ```

4. **Disable systemd sleep**:
   ```bash
   sudo systemctl mask sleep.target suspend.target hibernate.target
   ```

### Audio/Video Not Working

**Problem**: No audio output or webcam not detected

**Solutions**:

1. **Check PulseAudio**:
   ```bash
   pactl info
   pactl list sinks
   pactl list sources
   ```

2. **Test audio setup**:
   ```bash
   /home/pi/RaspberryMeet/scripts/test_audio_video.py
   ```

3. **Grant Chromium permissions**:
   - Camera/mic permissions are auto-granted with `--use-fake-ui-for-media-stream`
   - Check Chromium flags in `launch_kiosk_browser.sh`

4. **Check V4L2 devices**:
   ```bash
   v4l2-ctl --list-devices
   ```

### Auto-Login Not Working

**Problem**: Login prompt appears instead of auto-login

**Solutions**:

1. **Check LightDM config**:
   ```bash
   cat /etc/lightdm/lightdm.conf.d/50-raspberrymeet.conf
   ```

   Should contain:
   ```ini
   [Seat:*]
   autologin-user=pi
   autologin-user-timeout=0
   ```

2. **Verify user**:
   ```bash
   id pi
   ```

3. **Enable LightDM**:
   ```bash
   sudo systemctl enable lightdm
   sudo systemctl set-default graphical.target
   ```

4. **Reconfigure LightDM**:
   ```bash
   sudo dpkg-reconfigure lightdm
   ```

### Mouse Cursor Visible

**Problem**: Mouse cursor doesn't hide

**Solutions**:

1. **Install unclutter**:
   ```bash
   sudo apt-get install unclutter
   ```

2. **Check if running**:
   ```bash
   ps aux | grep unclutter
   ```

3. **Start manually**:
   ```bash
   export DISPLAY=:0
   unclutter -idle 5 -root &
   ```

4. **Alternative**: Hide cursor with CSS in web interface

### Remote Debugging

**Access Chromium DevTools remotely:**

1. **Chromium listens on port 9222** (configured in `launch_kiosk_browser.sh`)

2. **From another computer on same network**:
   ```
   http://raspberrypi.local:9222
   ```

3. **View live tabs and debug**:
   - Click on tab to open DevTools
   - Inspect DOM, console, network

---

## Advanced Configuration

### Custom Initial URL

Set initial URL when browser starts:

```bash
export KIOSK_INITIAL_URL="http://localhost:8080"
sudo systemctl restart raspberrymeet-kiosk
```

Or edit systemd service:

```ini
Environment="KIOSK_INITIAL_URL=http://localhost:8080"
```

### Multiple Displays

For dual-monitor setup:

```bash
# In .xinitrc, before launching browser
xrandr --output HDMI-1 --auto --primary
xrandr --output HDMI-2 --auto --right-of HDMI-1
```

### Touch Screen Support

For touch screen kiosks:

```bash
sudo apt-get install xserver-xorg-input-evdev
```

Calibrate touch:

```bash
sudo apt-get install xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

### Performance Mode

For better video performance:

Edit `/boot/config.txt`:

```ini
# GPU memory (minimum 128MB for video calls)
gpu_mem=256

# Overclock (Raspberry Pi 4)
over_voltage=2
arm_freq=1750

# Disable unnecessary features
dtoverlay=disable-wifi    # If using Ethernet
dtoverlay=disable-bt       # If not using Bluetooth
```

**Warning**: Overclocking may require heatsink/fan.

### Security Hardening

Restrict Chromium to specific domains:

Edit `launch_kiosk_browser.sh`, add to `CHROMIUM_FLAGS`:

```bash
--allow-running-insecure-content  # Only if needed
--host-rules="MAP * bbb.example.com"  # Restrict to BBB domain
```

### Scheduled Reboot

Reboot daily at 3 AM to clear memory:

```bash
sudo crontab -e
```

Add:

```cron
0 3 * * * /sbin/shutdown -r now
```

---

## Performance Tuning

### Chromium Flags Optimization

The `launch_kiosk_browser.sh` script includes optimized flags:

```bash
--disable-gpu-vsync                   # Reduce input lag
--disable-software-rasterizer         # Force GPU rendering
--enable-gpu-rasterization            # GPU compositing
--enable-zero-copy                    # Reduce memory copies
--disable-dev-shm-usage               # Prevent /dev/shm issues
```

### Hardware Acceleration

Verify GPU acceleration:

1. **Open remote debugging**: `http://raspberrypi.local:9222`
2. **Navigate to**: `chrome://gpu`
3. **Check**: "Graphics Feature Status"
   - WebGL: Hardware accelerated
   - Video Decode: Hardware accelerated

### Memory Management

Monitor memory usage:

```bash
# Real-time monitoring
htop

# Chromium memory
ps aux | grep chromium | awk '{sum+=$6} END {print sum/1024 " MB"}'
```

Limit Chromium memory:

```bash
# In systemd service
MemoryMax=2G
```

### Network Optimization

For better BBB performance:

```bash
# Increase network buffer sizes
sudo sysctl -w net.core.rmem_max=2097152
sudo sysctl -w net.core.wmem_max=2097152

# Make persistent
echo "net.core.rmem_max=2097152" | sudo tee -a /etc/sysctl.conf
echo "net.core.wmem_max=2097152" | sudo tee -a /etc/sysctl.conf
```

---

## Appendix: File Locations

### Configuration Files

```
/etc/lightdm/lightdm.conf.d/50-raspberrymeet.conf  # Auto-login
/home/pi/.xinitrc                                   # X11 startup
/home/pi/.config/openbox/autostart                  # Openbox autostart
/home/pi/.config/openbox/rc.xml                     # Openbox config
/boot/config.txt                                    # Raspberry Pi config
```

### Scripts

```
/home/pi/RaspberryMeet/scripts/setup_display.sh           # Display setup
/home/pi/RaspberryMeet/scripts/launch_kiosk_browser.sh    # Browser launcher
/home/pi/test_display.sh                                   # Test script
```

### Systemd Services

```
/etc/systemd/system/raspberrymeet-kiosk.service    # Kiosk browser service
```

### Logs

```
~/.local/share/xorg/Xorg.0.log         # X11 log
journalctl -u lightdm                  # LightDM log
journalctl -u raspberrymeet-kiosk      # Kiosk browser log
```

---

## Further Reading

- **X11 Configuration**: https://www.x.org/wiki/
- **Openbox Documentation**: http://openbox.org/wiki/Main_Page
- **LightDM Configuration**: https://wiki.archlinux.org/title/LightDM
- **Chromium Flags**: https://peter.sh/experiments/chromium-command-line-switches/
- **Raspberry Pi Display**: https://www.raspberrypi.org/documentation/configuration/config-txt/video.md

---

**Last Updated**: 2025-11-19
**RaspberryMeet Version**: 1.0.0

For issues or questions, open an issue on GitHub.
