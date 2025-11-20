# 🍓 RaspberryMeet

**Verwandeln Sie Ihren Raspberry Pi in ein professionelles BigBlueButton Meeting-Room-Gerät**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![Plattform](https://img.shields.io/badge/Plattform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![BBB Kompatibel](https://img.shields.io/badge/BBB-Kompatibel-success.svg)](https://bigbluebutton.org/)

> *Ein Meeting Computer, der eine günstige Nachstellung von professionellen Meetingboards abbilden soll.*

Eine kostengünstige Alternative zu teuren professionellen Meeting-Room-Systemen, angetrieben durch Raspberry Pi 4 und BigBlueButton. Ein-Knopf-Meeting-Beitritt, kalenderbasierte Automatisierung und freihändiger Betrieb—keine Tastatur oder Maus erforderlich.

[🇬🇧 English Version](README.md)

---

## 📸 Screenshots

*Demnächst: Web-Interface, Kiosk-Modus und Hardware-Setup-Fotos*

---

## ✨ Funktionen

### 🎯 Kernfunktionalität
- **🔘 Ein-Knopf-Beitritt** - GPIO-Button-Druck tritt sofort Ihrem BigBlueButton-Raum bei
- **📅 Kalender-Auto-Join** - Automatischer Beitritt zu Meetings aus Nextcloud/CalDAV-Kalendern
- **🌐 Web-Admin-Interface** - Meetings fernsteuern von jedem Gerät im Netzwerk
- **🖥️ Vollbild-Kiosk-Modus** - Chromium-Browser im ablenkungsfreien Vollbild
- **🎤 USB/Bluetooth-Audio** - Automatische Erkennung und Konfiguration von Konferenz-Freisprecheinrichtungen
- **📹 Webcam-Unterstützung** - Plug-and-Play USB-Webcam-Integration

### 🤖 Automatisierung
- **⚡ Auto-Login beim Booten** - Keine manuelle Interaktion erforderlich
- **🔄 Crash-Recovery** - Automatischer Browser-Neustart bei Fehlern
- **🕐 Geplante Meetings** - Beitritt 2 Minuten vor geplantem Start
- **💡 LED-Statusanzeigen** - Visuelle Rückmeldung (bereit/beitretend/aktiv/fehler)
- **🔇 GPIO Mute-Toggle** - Physischer Button für Stummschalten/Aktivieren

### 🔒 Privatsphäre & Sicherheit
- **🇪🇺 EU-First-Architektur** - Kompatibel mit EU-basierten BigBlueButton- und CalDAV-Servern
- **🔐 SHA-256-Passwort-Hashing** - Sichere Web-Interface-Authentifizierung
- **🚫 Keine Cloud-Abhängigkeiten** - Alle Daten bleiben lokal oder in Ihrer Infrastruktur
- **🔓 100% Open Source** - Keine proprietären Komponenten, kein Vendor Lock-in
- **❌ Kein Google/Microsoft** - Datenschutzfreundliche Alternative zu Google Meet/Teams-Geräten

### 🛠️ Systemverwaltung
- **📦 Ein-Befehl-Installation** - Komplettes Setup in 15-30 Minuten
- **🔄 Ein-Befehl-Updates** - Einfacher Upgrade-Prozess
- **📊 Systemd-Integration** - Professionelle Service-Verwaltung
- **📝 Umfassendes Logging** - Volle journalctl-Integration
- **🧪 Hardware-Test-Skripte** - GPIO, Audio, Video, Kalender validieren

---

## 🚀 Schnellstart

### Voraussetzungen

- **Raspberry Pi 4** (4GB+ RAM empfohlen)
- **Raspberry Pi OS** (Debian 11 Bullseye oder neuer)
- **Netzwerkverbindung** (Ethernet empfohlen)
- **HDMI-Display** (1080p empfohlen)
- **BigBlueButton-Server** (Zugang zu einer BBB-Instanz)

### Installation (15-30 Minuten)

```bash
# 1. Repository klonen
cd /home/pi
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet

# 2. Installations-Script ausführen
sudo ./scripts/install.sh
```

Der Installer wird:
- ✅ Alle System-Abhängigkeiten installieren (Python, Chromium, X11, PulseAudio)
- ✅ Python Virtual Environment einrichten
- ✅ Python-Pakete und Playwright installieren
- ✅ Kiosk-Modus und Auto-Login konfigurieren
- ✅ Systemd-Services installieren
- ✅ Konfigurationsdatei erstellen

### Konfiguration

Bearbeiten Sie `/home/pi/RaspberryMeet/.env`:

```bash
# Ihre BigBlueButton-Raum-URL
BBB_DEFAULT_ROOM_URL=https://bbb.example.com/b/ihr-raum-name
BBB_DEFAULT_ROOM_PASSWORD=ihr-raum-passwort

# Web-Interface-Passwort (nutzen Sie hash_password.py)
WEB_PASSWORD=sha256:ihr-gehashtes-passwort

# Optional: Kalender-Integration
CALDAV_ENABLED=true
CALDAV_URL=https://nextcloud.example.com/remote.php/dav
CALDAV_USERNAME=meeting-raum@example.com
CALDAV_PASSWORD=ihr-app-passwort
```

### Passwort-Hash generieren

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate
python scripts/hash_password.py
```

### Neustart

```bash
sudo reboot
```

Nach dem Neustart:
- ✅ System meldet sich automatisch an
- ✅ Chromium startet im Vollbild-Kiosk-Modus
- ✅ Grüne LED zeigt Bereitschaft an
- ✅ Web-Interface verfügbar unter `http://raspberrypi.local:8080`

---

## 📖 Dokumentation

Umfassende Anleitungen zu allen Aspekten:

| Anleitung | Beschreibung |
|-----------|--------------|
| [📥 INSTALLATION.md](INSTALLATION.md) | Vollständige Installations-Anleitung mit Fehlerbehebung |
| [🔧 GPIO_SETUP.md](GPIO_SETUP.md) | Hardware-Verkabelung, Buttons und LEDs |
| [🎵 AUDIO_VIDEO_SETUP.md](AUDIO_VIDEO_SETUP.md) | Freisprecheinrichtungs- und Webcam-Konfiguration |
| [📅 CALDAV_SETUP.md](CALDAV_SETUP.md) | Nextcloud/Radicale-Kalender-Integration |
| [🖥️ KIOSK_SETUP.md](KIOSK_SETUP.md) | Display-Konfiguration und Kiosk-Modus |
| [⚙️ AUTOSTART.md](AUTOSTART.md) | Systemd-Service-Verwaltung |
| [🤖 CLAUDE.md](CLAUDE.md) | AI-Assistenten-Entwicklungsanleitung |

---

## 🎮 Verwendung

### Via GPIO-Button
Drücken Sie den Join-Button → Meeting startet sofort

### Via Web-Interface
1. Browser öffnen: `http://raspberrypi.local:8080`
2. Mit Admin-Zugangsdaten anmelden
3. "Join Default Meeting" klicken

### Via Kalender
1. Event im Nextcloud-Kalender erstellen
2. BigBlueButton-URL in Beschreibung hinzufügen:
   ```
   Team Meeting

   Teilnehmen: https://bbb.example.com/b/team-meeting
   Passwort: geheim123
   ```
3. Meeting tritt automatisch 2 Minuten vor geplantem Start bei

---

## 🔧 Hardware-Setup

### Empfohlene Komponenten

| Komponente | Beispiel | Hinweise |
|------------|----------|----------|
| **Computer** | Raspberry Pi 4 (4GB) | Erforderlich |
| **ConferenceCam** | Logitech BCC950 ⭐ | All-in-One Webcam + Freisprecheinrichtung (empfohlen) |
| **Freisprecheinrichtung** | Jabra Speak 510 | USB oder Bluetooth Alternative |
| **Webcam** | Logitech C920 | 1080p empfohlen (bei separatem Gerät) |
| **Display** | Beliebiger HDMI-Monitor | 1920x1080 empfohlen |
| **Button** | Taktiler Druckknopf | GPIO 17 (Standard) |
| **LEDs** | Grün + Rot LEDs | GPIO 23/24 (Standard) |
| **Netzteil** | Offizielles RPi-Netzteil | 5V 3A empfohlen |

### GPIO-Pinbelegung (BCM-Nummerierung)

```
GPIO 17 → Join/Leave-Button
GPIO 22 → Mute-Toggle-Button (optional)
GPIO 23 → Status-LED Grün (bereit)
GPIO 24 → Status-LED Rot (im Meeting)
```

Vollständige Verkabelungsdiagramme in [GPIO_SETUP.md](GPIO_SETUP.md).

---

## 🔄 Updates

```bash
cd /home/pi/RaspberryMeet
sudo ./scripts/update.sh
```

Aktualisiert:
- ✅ Neuesten Code von Git
- ✅ Python-Pakete
- ✅ Playwright-Browser
- ✅ Systemd-Services

Ihre `.env`-Konfiguration wird automatisch gesichert.

---

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                      RaspberryMeet                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   GPIO       │  │  Kalender-   │  │   Web-API    │     │
│  │  Buttons     │  │  Scheduler   │  │  (FastAPI)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │             │
│         └─────────┬───────┴──────────────────┘             │
│                   ▼                                         │
│         ┌─────────────────────┐                            │
│         │  Meeting-Manager    │                            │
│         │  (Orchestrator)     │                            │
│         └─────────┬───────────┘                            │
│                   │                                         │
│         ┌─────────┴───────────┐                            │
│         ▼                     ▼                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Browser-   │      │    Audio-    │                   │
│  │ Controller   │      │   Manager    │                   │
│  │ (Playwright) │      │ (PulseAudio) │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────┐                                  │
│  │  Chromium Kiosk      │                                  │
│  │  (Vollbild BBB)      │                                  │
│  └──────────────────────┘                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testen

Einzelne Komponenten testen:

```bash
cd /home/pi/RaspberryMeet
source venv/bin/activate

# GPIO-Hardware testen
python scripts/test_gpio.py

# Audio/Video-Geräte testen
python scripts/test_audio_video.py

# Kalender-Sync testen
python scripts/test_calendar.py

# Display-Setup testen
./test_display.sh
```

Service-Logs anzeigen:

```bash
# Haupt-Orchestrator
journalctl -u raspberrymeet -f

# Web-Interface
journalctl -u raspberrymeet-web -f

# Kiosk-Browser
journalctl -u raspberrymeet-kiosk -f
```

---

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte siehe [CONTRIBUTING.md](CONTRIBUTING.md) für Richtlinien.

### Entwicklungs-Setup

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

- [x] BigBlueButton-Browser-Automatisierung
- [x] GPIO-Button/LED-Steuerung
- [x] Web-Admin-Interface
- [x] CalDAV-Kalender-Integration
- [x] Vollbild-Kiosk-Modus
- [x] Audio/Video-Geräte-Verwaltung
- [x] Systemd-Autostart
- [x] Ein-Befehl-Installation
- [ ] Mehrsprachige UI (Deutsch/Englisch)
- [ ] Prometheus-Metriken-Exporter
- [ ] Touchscreen-UI-Unterstützung
- [ ] SD-Karten-Image-Releases

---

## 🐛 Fehlerbehebung

### Service startet nicht

```bash
sudo systemctl status raspberrymeet
journalctl -u raspberrymeet -n 50
```

### Keine Audio-Ausgabe

```bash
pactl list sinks
./scripts/setup_audio.sh
```

### Kiosk-Modus startet nicht

```bash
sudo systemctl status raspberrymeet-kiosk
cat ~/.local/share/xorg/Xorg.0.log
```

Siehe [INSTALLATION.md](INSTALLATION.md#troubleshooting) für umfassende Fehlerbehebung.

---

## 🌟 Unterstützte Server

### BigBlueButton
Jeder BBB 2.4+ Server, einschließlich:
- Self-hosted BBB
- Managed BBB Hosting (Blindside Networks, senfcall.de, etc.)
- On-Premises-Installationen

### CalDAV
- ✅ Nextcloud (empfohlen)
- ✅ Radicale
- ✅ Baikal
- ✅ SOGo
- ❌ Google Calendar (Datenschutzbedenken)
- ❌ Microsoft 365 (Datenschutzbedenken)

---

## 📜 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE)-Datei für Details.

---

## 🙏 Danksagungen

- **BigBlueButton** - Open-Source-Webkonferenzen
- **Raspberry Pi Foundation** - Großartige Hardware-Plattform
- **Playwright** - Zuverlässige Browser-Automatisierung
- **FastAPI** - Modernes Python-Web-Framework
- **Nextcloud** - Datenschutzfreundliche Groupware

---

## 💬 Support

- 📖 **Dokumentation**: Siehe `/docs`-Ordner
- 🐛 **Fehlerberichte**: [GitHub Issues](https://github.com/Sico93/RaspberryMeet/issues)
- 💡 **Feature-Anfragen**: [GitHub Issues](https://github.com/Sico93/RaspberryMeet/issues)
- 📧 **Kontakt**: sico93@posteo.de

---

## ⭐ Star-Verlauf

Wenn Sie dieses Projekt nützlich finden, geben Sie ihm bitte einen Stern! ⭐

---

**Mit ❤️ für die Open-Source-Community gemacht**
