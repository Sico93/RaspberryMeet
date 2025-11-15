# RaspberryMeet

**Ein kostengünstiger Meeting-Computer für BigBlueButton-Konferenzen**

RaspberryMeet verwandelt einen Raspberry Pi 4 in ein einfach zu bedienendes Meeting-Room-System für BigBlueButton-Videokonferenzen. Mit nur einem Knopfdruck können Sie einem vordefinierten Meeting-Raum beitreten – ganz ohne Tastatur oder Maus.

## 🎯 Hauptfunktionen

- **Ein-Knopf-Beitritt:** GPIO-Button drücken → Sofort im BigBlueButton-Meeting
- **Kalender-Integration:** Automatischer Beitritt zu geplanten Meetings (CalDAV)
- **Web-Admin-Interface:** Steuerung und Konfiguration über Browser im lokalen Netzwerk
- **Hands-Free-Betrieb:** Keine Tastatur/Maus für Standardnutzung nötig
- **Privacy-First:** Nur Open Source, EU-gehostete Dienste

## 🔧 Hardware-Anforderungen

- **Raspberry Pi 4** (4GB+ empfohlen)
- **Konferenzspinne** (USB oder Bluetooth, z.B. Jabra Speak 510)
- **USB-Webcam** (z.B. Logitech C920)
- **GPIO-Buttons** (1-3 Taster für Meeting-Steuerung)
- **LEDs** (optional, für Statusanzeige)
- **HDMI-Monitor** (1080p empfohlen)
- **Netzwerk:** Ethernet bevorzugt

## 📦 Installation

**Voraussetzungen:**
- Raspberry Pi OS (Debian-basiert)
- Python 3.11+
- Zugang zu einem BigBlueButton-Server

### Schnellstart:

```bash
# Repository klonen
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet

# Abhängigkeiten installieren
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Playwright Browser installieren
playwright install chromium

# Konfiguration anpassen
cp .env.example .env
cp config/config.example.yaml config/config.yaml

# .env und config.yaml bearbeiten mit Ihren BBB-Zugangsdaten

# Web-Interface starten (Test)
python -m src.web.api

# Orchestrator starten
python -m src.orchestrator.main
```

Detaillierte Anleitung: Siehe [docs/SETUP.md](docs/SETUP.md)

## 🚀 Verwendung

### GPIO-Button-Nutzung (NEU!):

**Hardware-Verkabelung:**
- GPIO 17 (Pin 11): Join/Leave-Button
- GPIO 23 (Pin 16): Grüne Status-LED
- GPIO 24 (Pin 18): Rote Status-LED

**Bedienung:**
1. Raspberry Pi einschalten
2. **Grüne LED leuchtet** → System bereit
3. **Button drücken** → Gelbe LED → System tritt Meeting bei
4. **Rote LED leuchtet** → Im Meeting aktiv
5. **Button erneut drücken** → Gelbe LED → System verlässt Meeting
6. **Grüne LED leuchtet** → Wieder bereit

**LED-Status:**
- 🟢 Grün = Bereit für Meeting
- 🟡 Gelb (beide) = Trete bei / Verlasse
- 🔴 Rot = Im Meeting
- 🔴 Rot blinkend = Fehler

**Detaillierte Anleitung:** [GPIO_SETUP.md](GPIO_SETUP.md)

### Web-Interface-Nutzung:
1. Browser öffnen: `http://raspberrypi.local:8080`
2. Anmelden (Standard: admin/admin)
3. Dashboard zeigt aktuellen Status
4. "Join Meeting" Button klicken
5. Raum auswählen oder URL eingeben

### Kalender-Integration:
1. CalDAV-Server konfigurieren (Nextcloud, Radicale, etc.)
2. Meeting-Raum-Account zu Kalendertermin einladen
3. System tritt automatisch 1 Minute vor Start bei

## 🛠️ Konfiguration

### Umgebungsvariablen (`.env`):
```bash
BBB_SERVER_URL=https://bbb.example.eu/bigbluebutton/
BBB_API_SECRET=ihr-api-secret
BBB_DEFAULT_ROOM_URL=https://bbb.example.eu/b/standard-raum

CALDAV_URL=https://nextcloud.example.eu/remote.php/dav
CALDAV_USERNAME=meetingraum@example.eu
CALDAV_PASSWORD=ihr-passwort

WEB_USERNAME=admin
WEB_PASSWORD=sicheres-passwort
```

### GPIO-Pins anpassen (`config/gpio_pins.yaml`):
```yaml
buttons:
  join_default_meeting:
    gpio_bcm: 17  # Pin 11
  leave_meeting:
    gpio_bcm: 27  # Pin 13
```

Weitere Konfigurationsoptionen: Siehe [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

## 🧪 Aktuellen Stand auf Raspberry Pi testen

**Schnellanleitung zum Testen der BBB-Automation:**

📋 **[RASPBERRY_PI_TEST.md](RASPBERRY_PI_TEST.md)** - Schritt-für-Schritt Anleitung zum Testen auf dem Raspberry Pi

**Kurzfassung:**
```bash
# 1. Repository klonen
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet
git checkout claude/claude-md-mi0ls28jefrj31gk-01Fy51p4K9pYPy9KWyM2Uw6R

# 2. Dependencies installieren
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. Konfigurieren
cp .env.example .env
nano .env  # BBB_DEFAULT_ROOM_URL anpassen

# 4. Demo starten
python demo_bbb_join.py
```

Der Browser sollte automatisch Ihren BBB-Raum öffnen und beitreten!

## 🌐 Web Admin Interface (NEU!)

**Steuern Sie Meetings über Ihren Browser im lokalen Netzwerk!**

📋 **[WEB_INTERFACE.md](WEB_INTERFACE.md)** - Vollständige Web-Interface-Dokumentation

**Schnellstart Web-Interface:**
```bash
# Nach Installation (siehe oben):
python run_web.py

# Im Browser öffnen:
# http://raspberrypi.local:8080
# Benutzername: admin
# Passwort: (aus .env konfigurieren)
```

**Features:**
- 🚀 Ein-Klick-Join zum Standard-Meeting
- 🔗 Benutzerdefinierte BBB-Raum-URLs
- 📊 Echtzeit-Status mit WebSocket
- ⏱️ Live Meeting-Dauer
- 📱 Mobile-responsive
- 🔐 Passwortgeschützt

## 📖 Dokumentation

- **[GPIO_SETUP.md](GPIO_SETUP.md)** - 🔌 **GPIO Hardware-Setup & Verkabelung** (NEU!)
- **[WEB_INTERFACE.md](WEB_INTERFACE.md)** - 🌐 **Web Admin Interface Guide**
- **[RASPBERRY_PI_TEST.md](RASPBERRY_PI_TEST.md)** - 🎯 **Test-Anleitung für Raspberry Pi**
- **[SETUP.md](docs/SETUP.md)** - Vollständige Installationsanleitung
- **[HARDWARE.md](docs/HARDWARE.md)** - GPIO-Verkabelung und Hardware-Setup
- **[CALDAV_SETUP.md](docs/CALDAV_SETUP.md)** - Kalender-Integration einrichten
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Häufige Probleme und Lösungen
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Benutzerhandbuch

## 🏗️ Projektstruktur

```
RaspberryMeet/
├── src/
│   ├── orchestrator/       # Haupt-Orchestrator-Service
│   ├── web/                # Web-Admin-Interface (FastAPI)
│   ├── models/             # Datenmodelle
│   └── utils/              # Hilfsfunktionen
├── tests/                  # Unit- und Integrationstests
├── config/                 # Konfigurationsdateien
├── systemd/                # Systemd-Service-Definitionen
├── scripts/                # Setup- und Deployment-Skripte
├── docs/                   # Dokumentation
└── hardware/               # Hardware-Schaltpläne und Specs
```

## 🔒 Sicherheit & Datenschutz

- **Nur Open Source:** Alle Komponenten sind quelloffen
- **EU-Server:** CalDAV und BBB-Server können EU-gehostet werden
- **Local-First:** Konfiguration lokal gespeichert
- **Keine Cloud-Abhängigkeit:** Funktioniert komplett offline (außer BBB-Verbindung)

## 🤝 Beitragen

Beiträge sind willkommen! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

### Entwicklung:

```bash
# Entwicklungsabhängigkeiten installieren
pip install -r requirements-dev.txt

# Pre-commit Hooks einrichten
pre-commit install

# Tests ausführen
pytest

# Code-Qualität prüfen
black src/ tests/
ruff check src/ tests/
mypy src/
```

## 📝 Lizenz

[MIT License](LICENSE)

## 👤 Autor

**Sico93** (sico93@posteo.de)

## 🙏 Danksagungen

- [BigBlueButton](https://bigbluebutton.org/) - Open Source Web-Konferenz-Plattform
- [PiMeet](https://github.com/pmansour/pimeet) - Inspiration für Kiosk-Architektur
- [Playwright](https://playwright.dev/) - Browser-Automatisierung
- [FastAPI](https://fastapi.tiangolo.com/) - Modernes Python-Web-Framework

## 🔗 Links

- **BigBlueButton:** https://docs.bigbluebutton.org/
- **Raspberry Pi:** https://www.raspberrypi.org/
- **CLAUDE.md:** Siehe [CLAUDE.md](CLAUDE.md) für AI-Entwickler-Dokumentation

---

**Status:** 🚧 In Entwicklung (v0.1.0-alpha)

Letzte Aktualisierung: 2025-11-15
