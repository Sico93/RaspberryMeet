# 🍓 RaspberryMeet

**Transform your Raspberry Pi into a professional BigBlueButton meeting room device**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![BBB Compatible](https://img.shields.io/badge/BBB-Compatible-success.svg)](https://bigbluebutton.org/)

> *Ein Meeting Computer, der eine günstige Nachstellung von professionellen Meetingboards abbilden soll.*

A cost-effective alternative to expensive professional meeting room systems, powered by Raspberry Pi 4 and BigBlueButton. One-button meeting joins, calendar-based automation, and hands-free operation—no keyboard or mouse required.

[🇩🇪 Deutsche Version](README.de.md)

---

## 📸 Screenshots

*Coming soon: Web interface, kiosk mode, and hardware setup photos*

---

## ✨ Features

### 🎯 Core Functionality
- **🔘 One-Button Join** - GPIO button press instantly joins your BigBlueButton room
- **📅 Calendar Auto-Join** - Automatically join meetings from Nextcloud/CalDAV calendars
- **🌐 Web Admin Interface** - Control meetings remotely from any device on your network
- **🖥️ Fullscreen Kiosk Mode** - Chromium browser in distraction-free fullscreen
- **🎤 USB/Bluetooth Audio** - Automatic detection and configuration of conference speakerphones
- **📹 Webcam Support** - Plug-and-play USB webcam integration

### 🤖 Automation
- **⚡ Auto-Login on Boot** - No manual interaction needed
- **🔄 Crash Recovery** - Automatic browser restart on failures
- **🕐 Scheduled Meetings** - Join meetings 2 minutes before scheduled start
- **💡 LED Status Indicators** - Visual feedback (idle/joining/active/error)
- **🔇 GPIO Mute Toggle** - Physical button for mute/unmute

### 🔒 Privacy & Security
- **🇪🇺 EU-First Architecture** - Compatible with EU-based BigBlueButton and CalDAV servers
- **🔐 SHA-256 Password Hashing** - Secure web interface authentication
- **🚫 No Cloud Dependencies** - All data stays local or in your infrastructure
- **🔓 100% Open Source** - No proprietary components, no vendor lock-in
- **❌ No Google/Microsoft** - Privacy-friendly alternative to Google Meet/Teams devices

### 🛠️ System Management
- **📦 One-Command Installation** - Complete setup in 15-30 minutes
- **🔄 One-Command Updates** - Simple upgrade process
- **📊 Systemd Integration** - Professional service management
- **📝 Comprehensive Logging** - Full journalctl integration
- **🧪 Hardware Testing Scripts** - Validate GPIO, audio, video, calendar

---

## 🚀 Quick Start

### Prerequisites

- **Raspberry Pi 4** (4GB+ RAM recommended)
- **Raspberry Pi OS** (Debian 11 Bullseye or newer)
- **Network connection** (Ethernet recommended)
- **HDMI display** (1080p recommended)
- **BigBlueButton server** (access to a BBB instance)

### Installation (15-30 minutes)

```bash
# 1. Clone repository
cd /home/pi
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet

# 2. Run installation script
sudo ./scripts/install.sh
```

The installer will:
- ✅ Install all system dependencies (Python, Chromium, X11, PulseAudio)
- ✅ Set up Python virtual environment
- ✅ Install Python packages and Playwright
- ✅ Configure kiosk mode and auto-login
- ✅ Install systemd services
- ✅ Create configuration file

### Configuration

Edit `/home/pi/RaspberryMeet/.env`:

```bash
# Your BigBlueButton room URL
BBB_DEFAULT_ROOM_URL=https://bbb.example.com/b/your-room-name
BBB_DEFAULT_ROOM_PASSWORD=your-room-password

# Web interface password (use hash_password.py)
WEB_PASSWORD=sha256:your-hashed-password

# Optional: Calendar integration
CALDAV_ENABLED=true
CALDAV_URL=https://nextcloud.example.com/remote.php/dav
CALDAV_USERNAME=meeting-room@example.com
CALDAV_PASSWORD=your-app-password
```

### Generate Password Hash

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/hash_password.py
```

### Reboot

```bash
sudo reboot
```

After reboot:
- ✅ System auto-logs in
- ✅ Chromium starts in fullscreen kiosk mode
- ✅ Green LED indicates ready state
- ✅ Web interface available at `http://raspberrypi.local:8080`

---

## 📖 Documentation

Comprehensive guides covering all aspects:

| Guide | Description |
|-------|-------------|
| [📥 INSTALLATION.md](INSTALLATION.md) | Complete installation guide with troubleshooting |
| [🔧 GPIO_SETUP.md](GPIO_SETUP.md) | Hardware wiring, buttons, and LEDs |
| [🎵 AUDIO_VIDEO_SETUP.md](AUDIO_VIDEO_SETUP.md) | Speakerphone and webcam configuration |
| [📅 CALDAV_SETUP.md](CALDAV_SETUP.md) | Nextcloud/Radicale calendar integration |
| [🖥️ KIOSK_SETUP.md](KIOSK_SETUP.md) | Display configuration and kiosk mode |
| [⚙️ AUTOSTART.md](AUTOSTART.md) | Systemd service management |
| [🤖 CLAUDE.md](CLAUDE.md) | AI assistant development guide |

---

## 🎮 Usage

### Via GPIO Button
Press the join button → Meeting starts instantly

### Via Web Interface
1. Open browser: `http://raspberrypi.local:8080`
2. Login with admin credentials
3. Click "Join Default Meeting"

### Via Calendar
1. Create event in Nextcloud calendar
2. Add BigBlueButton URL in description:
   ```
   Team Meeting

   Join: https://bbb.example.com/b/team-meeting
   Password: secret123
   ```
3. Meeting auto-joins 2 minutes before scheduled start

---

## 🔧 Hardware Setup

### Recommended Components

| Component | Example | Notes |
|-----------|---------|-------|
| **Computer** | Raspberry Pi 4 (4GB) | Required |
| **Speakerphone** | Jabra Speak 510 | USB or Bluetooth |
| **Webcam** | Logitech C920 | 1080p recommended |
| **Display** | Any HDMI monitor | 1920x1080 recommended |
| **Button** | Tactile push button | GPIO 17 (default) |
| **LEDs** | Green + Red LEDs | GPIO 23/24 (default) |
| **Power** | Official RPi PSU | 5V 3A recommended |

### GPIO Pinout (BCM numbering)

```
GPIO 17 → Join/Leave Button
GPIO 22 → Mute Toggle Button (optional)
GPIO 23 → Status LED Green (ready)
GPIO 24 → Status LED Red (in meeting)
```

Full wiring diagrams in [GPIO_SETUP.md](GPIO_SETUP.md).

---

## 🔄 Updates

```bash
cd /home/pi/RaspberryMeet
sudo ./scripts/update.sh
```

Updates:
- ✅ Latest code from Git
- ✅ Python packages
- ✅ Playwright browser
- ✅ Systemd services

Your `.env` configuration is automatically backed up.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      RaspberryMeet                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GPIO       │  │  Calendar    │  │   Web API    │     │
│  │  Buttons     │  │  Scheduler   │  │  (FastAPI)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │             │
│         └─────────┬───────┴──────────────────┘             │
│                   ▼                                         │
│         ┌─────────────────────┐                            │
│         │  Meeting Manager    │                            │
│         │  (Orchestrator)     │                            │
│         └─────────┬───────────┘                            │
│                   │                                         │
│         ┌─────────┴───────────┐                            │
│         ▼                     ▼                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Browser    │      │    Audio     │                   │
│  │ Controller   │      │   Manager    │                   │
│  │ (Playwright) │      │ (PulseAudio) │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────┐                                  │
│  │  Chromium Kiosk      │                                  │
│  │  (Fullscreen BBB)    │                                  │
│  └──────────────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

Test individual components:

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate

# Test GPIO hardware
python scripts/test_gpio.py

# Test audio/video devices
python scripts/test_audio_video.py

# Test calendar sync
python scripts/test_calendar.py

# Test display setup
./test_display.sh
```

View service logs:

```bash
# Main orchestrator
journalctl -u raspberrymeet -f

# Web interface
journalctl -u raspberrymeet-web -f

# Kiosk browser
journalctl -u raspberrymeet-kiosk -f
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## 📋 Roadmap

- [x] BigBlueButton browser automation
- [x] GPIO button/LED control
- [x] Web admin interface
- [x] CalDAV calendar integration
- [x] Fullscreen kiosk mode
- [x] Audio/video device management
- [x] Systemd autostart
- [x] One-command installation
- [ ] Multi-language UI (German/English)
- [ ] Prometheus metrics exporter
- [ ] Touch screen UI support
- [ ] SD card image releases

---

## 🐛 Troubleshooting

### Service won't start

```bash
sudo systemctl status raspberrymeet
journalctl -u raspberrymeet -n 50
```

### No audio output

```bash
pactl list sinks
./scripts/setup_audio.sh
```

### Kiosk mode not starting

```bash
sudo systemctl status raspberrymeet-kiosk
cat ~/.local/share/xorg/Xorg.0.log
```

See [INSTALLATION.md](INSTALLATION.md#troubleshooting) for comprehensive troubleshooting.

---

## 🌟 Supported Servers

### BigBlueButton
Any BBB 2.4+ server, including:
- Self-hosted BBB
- Managed BBB hosting (Blindside Networks, senfcall.de, etc.)
- On-premises installations

### CalDAV
- ✅ Nextcloud (recommended)
- ✅ Radicale
- ✅ Baikal
- ✅ SOGo
- ❌ Google Calendar (privacy concerns)
- ❌ Microsoft 365 (privacy concerns)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **BigBlueButton** - Open source web conferencing
- **Raspberry Pi Foundation** - Amazing hardware platform
- **Playwright** - Reliable browser automation
- **FastAPI** - Modern Python web framework
- **Nextcloud** - Privacy-friendly groupware

---

## 💬 Support

- 📖 **Documentation**: See `/docs` folder
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/Sico93/RaspberryMeet/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/Sico93/RaspberryMeet/issues)
- 📧 **Contact**: sico93@posteo.de

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ for the open source community**
