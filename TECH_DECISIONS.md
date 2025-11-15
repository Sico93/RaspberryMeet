# RaspberryMeet - Technologie-Entscheidungen

**Datum:** 2025-11-15
**Projekt:** BigBlueButton Kiosk Client für Raspberry Pi

---

## Übersicht

Dieses Dokument erklärt die wichtigsten technologischen Entscheidungen für das RaspberryMeet-Projekt und die Gründe dahinter.

---

## 1. Architektur-Muster: Kiosk + Orchestrator

**Entscheidung:** Chromium-Browser im Kiosk-Modus + Python-Orchestrator-Service

**Alternativen erwogen:**
- Native BBB-Client entwickeln (WebRTC in Python/C++)
- Electron-App mit eingebautem Browser
- VNC-basierte Remote-Desktop-Lösung

**Begründung:**
- **Wartbarkeit:** BBB läuft nativ im Browser, keine Reimplementierung von WebRTC nötig
- **Feature-Parität:** Alle BBB-Features (Screenshare, Chat, Breakout-Rooms) funktionieren
- **Bewährtes Konzept:** PiMeet-Projekt zeigt, dass Browser-Automation auf Pi funktioniert
- **Geringere Komplexität:** Keine Eigenentwicklung von Audio/Video-Codecs

**Nachteile (akzeptiert):**
- Browser-Overhead (~300-500 MB RAM)
- Abhängigkeit von BBB-UI-Stabilität
- Chromium-Updates können Selektoren brechen

**Mitigation:**
- Pi 4 hat genug RAM (4GB)
- Flexible Selektoren mit Fallbacks
- Versionierung der getesteten BBB-Version

---

## 2. Browser-Automation: Playwright

**Entscheidung:** Playwright statt Selenium

**Vergleich:**

| Kriterium | Playwright | Selenium |
|-----------|-----------|----------|
| Performance | ⭐⭐⭐⭐⭐ Schneller | ⭐⭐⭐ Langsamer |
| API-Design | ⭐⭐⭐⭐⭐ Modern, async | ⭐⭐⭐ Älter, synchron |
| Auto-Waiting | ⭐⭐⭐⭐⭐ Eingebaut | ⭐⭐ Manuell |
| Test-Stabilität | ⭐⭐⭐⭐⭐ Weniger flaky | ⭐⭐⭐ Oft flaky |
| Community | ⭐⭐⭐ Wachsend | ⭐⭐⭐⭐⭐ Riesig |
| ARM-Support | ⭐⭐⭐⭐⭐ Offiziell | ⭐⭐⭐⭐ Funktioniert |
| Download-Größe | ⭐⭐⭐ ~300 MB | ⭐⭐⭐⭐ ~150 MB |

**Begründung:**
- **Bessere Developer-Experience:** Async/await ist natürlicher in Python 3.11+
- **Robustheit:** Auto-waiting reduziert Race-Conditions dramatisch
- **Zukunftssicher:** Playwright ist aktiv entwickelt (Microsoft-backed)
- **Debugging:** Bessere Error-Messages und Screenshots

**Fallback-Plan:**
Falls Playwright auf Pi problematisch ist:
- Selenium + `undetected-chromedriver` als Alternative
- Beide verwenden ähnliche Konzepte (Page Objects), Migration einfach

---

## 3. Programmiersprache: Python 3.11+

**Entscheidung:** Python statt Node.js oder Go

**Begründung:**
- **GPIO-Support:** Exzellente Libraries (gpiozero, RPi.GPIO)
- **Raspberry Pi Ökosystem:** Beste Integration (Raspbian, Tutorials)
- **Browser-Automation:** Playwright und Selenium haben Python-Bindings
- **CalDAV:** Reife Libraries (caldav, icalendar)
- **Entwickler-Komfort:** Einfache Syntax, schnelles Prototyping

**Warum nicht Node.js:**
- GPIO-Libraries weniger ausgereift
- Async-Callback-Hell bei komplexen Workflows
- Weniger Ressourcen für Pi-spezifische Probleme

**Warum nicht Go:**
- GPIO-Support experimentell
- Kleineres Ökosystem für CalDAV/Browser-Automation
- Längere Entwicklungszeit für Prototyping

---

## 4. Kalender-Protokoll: CalDAV

**Entscheidung:** CalDAV (open standard) statt proprietäre APIs

**Alternativen verworfen:**
- ❌ **Google Calendar API:** USA-basiert, DSGVO-problematisch, OAuth-Komplexität
- ❌ **Microsoft Graph API:** USA-basiert, Azure-Lock-in
- ❌ **IMAP-basiert (Outlook):** Kein Standard für Kalender

**Begründung:**
- **Privacy-First:** EU-hostbare Server (Nextcloud, Radicale)
- **Open Standard:** RFC 4791, keine Vendor-Lock-in
- **Einfachheit:** HTTP-basiert, BasicAuth möglich
- **Offline-Fähigkeit:** Events lokal cachebar
- **Flexibilität:** Jede CalDAV-Software funktioniert (Nextcloud, Thunderbird, DAVx5)

**Empfohlene Server:**
1. **Nextcloud** - Für Organisationen (Web-UI, Mobile-Apps)
2. **Radicale** - Für Minimalisten (Python, dateibasiert)
3. **Baikal** - Für Webspace-Hoster (PHP, einfach)

---

## 5. Audio-Stack: PulseAudio

**Entscheidung:** PulseAudio statt ALSA direkt

**Begründung:**
- **Device-Management:** Hot-Plugging von USB/Bluetooth-Geräten
- **Automatic Routing:** Default-Device-Switching ohne Code
- **Browser-Kompatibilität:** Chromium nutzt PulseAudio nativ
- **Mixing:** Mehrere Apps können gleichzeitig Audio nutzen
- **Bluetooth:** Nahtlose Integration über bluez

**ALSA-Rolle:**
- Low-Level Backend für PulseAudio
- Nur für Debugging direkt nutzen

**Alternative (verworfen):**
- **JACK:** Zu komplex für Use-Case, Pro-Audio-fokussiert
- **PipeWire:** Zu neu, weniger Pi-Dokumentation (2025 noch nicht stable genug)

---

## 6. GPIO-Library: gpiozero

**Entscheidung:** gpiozero statt RPi.GPIO

**Vergleich:**

| Feature | gpiozero | RPi.GPIO |
|---------|----------|----------|
| API-Level | ⭐⭐⭐⭐⭐ High-level | ⭐⭐ Low-level |
| Code-Lesbarkeit | ⭐⭐⭐⭐⭐ Sehr klar | ⭐⭐⭐ Verbose |
| Debouncing | ⭐⭐⭐⭐⭐ Eingebaut | ⭐⭐ Manuell |
| Event-Callbacks | ⭐⭐⭐⭐⭐ when_pressed | ⭐⭐⭐ add_event_detect |
| Mock-Support | ⭐⭐⭐⭐⭐ PinFactory | ⭐⭐ Selbst bauen |
| Dokumentation | ⭐⭐⭐⭐⭐ Exzellent | ⭐⭐⭐⭐ Gut |

**Code-Beispiel Vergleich:**

**gpiozero:**
```python
from gpiozero import Button, LED

button = Button(17)
led = LED(23)

button.when_pressed = lambda: led.on()
button.when_released = lambda: led.off()
```

**RPi.GPIO:**
```python
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.OUT)

def button_callback(channel):
    if GPIO.input(17) == GPIO.LOW:
        GPIO.output(23, GPIO.HIGH)
    else:
        GPIO.output(23, GPIO.LOW)

GPIO.add_event_detect(17, GPIO.BOTH, callback=button_callback, bouncetime=200)
```

**Urteil:** gpiozero ist klar überlegen für diesen Use-Case.

---

## 7. Konfiguration: YAML

**Entscheidung:** YAML statt JSON oder TOML

**Begründung:**
- **Lesbarkeit:** Kommentare möglich, menschenfreundlich
- **Hierarchie:** Verschachtelte Strukturen natürlich darstellbar
- **Standard:** Weit verbreitet (Kubernetes, Docker-Compose, Ansible)
- **Python-Support:** PyYAML ist stabil und ausgereift

**Beispiel-Config:**
```yaml
# config/config.yaml
bbb:
  server_url: https://bbb.example.eu
  default_room:
    url: https://bbb.example.eu/b/abc-def
    password: secretpassword
    username: "Meeting-Room-1"

gpio:
  buttons:
    join_button: 17
    leave_button: 27
  leds:
    status_green: 23
    status_red: 24

calendar:
  enabled: true
  caldav_url: https://nextcloud.example.eu/remote.php/dav
  username: room1@example.eu
  sync_interval_minutes: 5

audio:
  preferred_device: "Jabra Speak 510"
  fallback_to_hdmi: true

logging:
  level: INFO
  file: /var/log/raspberrymeet/app.log
```

**Warum nicht JSON:**
- Keine Kommentare möglich
- Trailing Commas problematisch

**Warum nicht TOML:**
- Weniger verbreitet
- Tiefe Verschachtelung unhandlich

---

## 8. Service-Management: systemd

**Entscheidung:** systemd statt supervisord oder pm2

**Begründung:**
- **Native Integration:** Raspbian/Debian Standard
- **Journald-Logging:** Zentrales Log-Management mit `journalctl`
- **Dependencies:** Elegante Service-Abhängigkeiten (After=, Requires=)
- **Auto-Restart:** Eingebautes Crash-Recovery
- **Boot-Integration:** Nahtlose Integration mit System-Boot

**Service-Dateien:**
- `raspberrymeet.service` - Haupt-Orchestrator
- `raspberrymeet-kiosk.service` - Chromium-Browser
- `raspberrymeet-setup.service` - Einmalige Boot-Checks

**Warum nicht supervisord:**
- Zusätzliche Dependency
- Weniger System-Integration

**Warum nicht Docker:**
- GPIO-Zugriff komplizierter
- Overhead unnötig für Single-Purpose-Device
- Image-Größe für SD-Card problematisch

---

## 9. Testing: pytest

**Entscheidung:** pytest statt unittest

**Begründung:**
- **Fixtures:** Elegante Setup/Teardown-Verwaltung
- **Parametrisierung:** Einfache Test-Varianten
- **Plugins:** pytest-cov, pytest-mock, pytest-asyncio
- **Assertions:** Keine `self.assertEqual`, einfaches `assert`
- **Discovery:** Auto-findet Tests

**Test-Struktur:**
```
tests/
├── unit/
│   ├── test_meeting_manager.py
│   ├── test_gpio_handler.py
│   └── test_calendar_sync.py
├── integration/
│   ├── test_bbb_join.py
│   └── test_full_workflow.py
└── fixtures/
    ├── sample_config.yaml
    └── sample_calendar.ics
```

---

## 10. Versionskontrolle: Git + Semantic Versioning

**Entscheidung:** Git mit Conventional Commits + SemVer

**Commit-Format:**
```
<type>(<scope>): <subject>

feat(gpio): add long-press detection for buttons
fix(browser): handle BBB connection timeout
docs(setup): add CalDAV configuration guide
```

**Versionierung:**
- **v0.1.0** - MVP (GPIO-Button + BBB-Join)
- **v0.2.0** - CalDAV-Integration
- **v0.3.0** - Kiosk-Modus
- **v1.0.0** - Production-Ready

**Branching:**
- `main` - Stable releases
- `develop` - Integration branch
- `feature/*` - Neue Features
- `bugfix/*` - Bugfixes
- `claude/*` - AI-generierte Branches

---

## 11. Lizenz: MIT (empfohlen)

**Entscheidung:** MIT License (zu bestätigen durch Projektinhaber)

**Begründung:**
- **Permissive:** Kommerzielle Nutzung erlaubt
- **Einfach:** Kurz und verständlich
- **Verbreitung:** Fork-freundlich
- **Attribution:** Autor bleibt genannt

**Alternative:**
- **GPL v3:** Wenn Copyleft gewünscht (abgeleitete Werke müssen auch GPL sein)
- **AGPL v3:** Wenn auch Web-Services unter Copyleft fallen sollen

**Rechtlicher Hinweis:** Lizenzentscheidung muss vom Projektinhaber (Sico93) getroffen werden.

---

## 12. Deployment-Strategie: Bash-Script + Ansible (später)

**Phase 1 (Sofort):** Bash-Installations-Script

```bash
#!/bin/bash
# scripts/install.sh

set -e  # Exit on error

echo "🚀 Installing RaspberryMeet..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv chromium-browser git

# Create virtualenv
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Setup systemd services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Configure
cp config/config.example.yaml config/config.yaml
echo "✏️  Edit config/config.yaml with your BBB credentials"

echo "✅ Installation complete!"
```

**Phase 2 (Später):** Ansible Playbook für Multi-Device-Rollout

```yaml
# deploy.yml
- hosts: raspberry_meet_devices
  tasks:
    - name: Install RaspberryMeet
      git:
        repo: https://github.com/Sico93/RaspberryMeet
        dest: /opt/raspberrymeet
    - name: Run install script
      command: /opt/raspberrymeet/scripts/install.sh
```

---

## 13. Hardware-Spezifikationen

**Minimale Hardware:**
- **Raspberry Pi 4B 4GB** - CPU/RAM für Chromium
- **SanDisk Extreme 32GB microSD** - A2-Rating für IOPS
- **Offizielles Pi 4 Netzteil (5.1V 3A)** - Stabil für USB-Geräte
- **Beliebige USB-Webcam** - V4L2-kompatibel (Logitech C920 empfohlen)
- **USB-Konferenzspinne** - Siehe empfohlene Modelle unten
- **GPIO-Buttons** - Standard Taster, 3.3V kompatibel
- **LEDs** - 3mm/5mm LEDs + 220Ω Widerstände

**Empfohlene Konferenzspinnen:**

| Modell | Anschluss | Echo-Cancellation | Preis (ca.) | Notizen |
|--------|-----------|-------------------|-------------|---------|
| Jabra Speak 510 | USB | ⭐⭐⭐⭐⭐ | 120€ | Beste Wahl, getestet |
| Anker PowerConf | USB | ⭐⭐⭐⭐ | 100€ | Budget-Option |
| eMeet M2 | USB/BT | ⭐⭐⭐⭐ | 80€ | Gut für <5 Personen |
| Logitech P710e | USB | ⭐⭐⭐ | 90€ | Älter, aber stabil |

**Bluetooth-Hinweis:** USB wird empfohlen (weniger Latenz, stabiler). Bluetooth als Fallback.

---

## 14. Netzwerk: Ethernet > WiFi

**Empfehlung:** Ethernet-Kabel, kein WiFi

**Begründung:**
- **Latenz:** 2-5ms vs. 20-50ms (WiFi)
- **Stabilität:** Keine Interferenzen, keine Reconnects
- **Bandbreite:** Volle 1Gbit/s (Pi 4) vs. ~300Mbit/s (WiFi)
- **Zuverlässigkeit:** Wichtig für Video-Konferenzen

**WiFi-Konfiguration (Fallback):**
```bash
# /etc/wpa_supplicant/wpa_supplicant.conf
network={
    ssid="YourNetworkName"
    psk="YourPassword"
    priority=1
}
```

**Empfehlung:** Statische IP für einfacheren Support

```bash
# /etc/dhcpcd.conf
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

---

## 15. Sicherheit: Defense-in-Depth

**Layers:**

1. **Netzwerk-Level:**
   - Firewall (ufw): Nur BBB + CalDAV + SSH
   - VPN für Remote-Management (optional)
   - Kein Internet-Zugang außer Whitelist

2. **System-Level:**
   - Minimale Packages (kein X11-Display-Manager, nur Xorg)
   - Auto-Updates für Security-Patches
   - Non-root Services (User: raspberrymeet)

3. **Application-Level:**
   - Secrets in Environment-Variables (nicht in Git)
   - Config-Validierung beim Start
   - Input-Sanitization für Calendar-URLs

4. **Physical-Level:**
   - SD-Card Read-Only-Mode (nach Konfiguration)
   - GPIO-Panic-Button (Hard-Reset)
   - Gehäuse mit Sicherheitsschrauben (optional)

**UFW-Konfiguration:**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH (nur wenn nötig)
sudo ufw enable
```

---

## 16. Web-Framework: FastAPI

**Entscheidung:** FastAPI statt Flask oder Django

**Vergleich:**

| Kriterium | FastAPI | Flask | Django |
|-----------|---------|-------|--------|
| Performance | ⭐⭐⭐⭐⭐ Async, schnell | ⭐⭐⭐ Synchron | ⭐⭐⭐ Synchron, schwerer |
| Async Support | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Mit Quart | ⭐⭐⭐ Mit Channels |
| API-First | ⭐⭐⭐⭐⭐ Built-in | ⭐⭐⭐ Manuell | ⭐⭐ REST Framework nötig |
| Auto-Docs | ⭐⭐⭐⭐⭐ OpenAPI/Swagger | ⭐ Manuell | ⭐ Manuell |
| Type Hints | ⭐⭐⭐⭐⭐ Required | ⭐⭐ Optional | ⭐⭐ Optional |
| Lernkurve | ⭐⭐⭐⭐ Einfach | ⭐⭐⭐⭐⭐ Sehr einfach | ⭐⭐ Komplex |
| Overhead | ⭐⭐⭐⭐ Klein | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐ Groß |
| WebSocket | ⭐⭐⭐⭐⭐ Built-in | ⭐⭐ Extension | ⭐⭐⭐ Channels |

**Begründung:**
- **Async-First:** Passt perfekt zu asyncio-basierten Orchestrator
- **Type Safety:** Pydantic-Integration für validierte Config/Requests
- **Auto-Documentation:** `/docs` Endpoint mit Swagger UI automatisch
- **Modern:** Aktiv entwickelt, zukunftssicher
- **Lightweight:** Kein ORM-Overhead (brauchen wir nicht)
- **WebSocket Support:** Für zukünftige Real-Time-Updates

**Frontend-Strategie:**
- **Jinja2 Templates:** Server-Side-Rendering für HTML
- **htmx:** Partial-Page-Updates ohne Full-JavaScript-Framework
- **Alpine.js** (optional): Minimales JavaScript für Interaktivität
- **No Build Step:** Direkte Entwicklung ohne npm/webpack

**Beispiel-API:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class MeetingJoinRequest(BaseModel):
    room_url: str
    username: str = "RaspberryMeet"

@app.get("/api/status")
async def get_status():
    """Aktueller Meeting-Status"""
    return {
        "state": "idle",  # idle, joining, active
        "current_meeting": None,
        "uptime": 3600
    }

@app.post("/api/meeting/join")
async def join_meeting(request: MeetingJoinRequest):
    """Meeting beitreten"""
    # Trigger orchestrator via IPC
    await meeting_manager.join(request.room_url, request.username)
    return {"status": "joining"}
```

**htmx-Beispiel:**
```html
<!-- Dashboard mit Auto-Refresh -->
<div hx-get="/api/status" hx-trigger="every 2s" hx-swap="innerHTML">
  <p>Status: <span id="state">Lädt...</span></p>
</div>

<!-- Quick-Join-Button -->
<button
  hx-post="/api/meeting/join"
  hx-vals='{"room_url": "https://bbb.example.eu/b/default-room"}'
  class="btn-primary">
  Standard-Meeting beitreten
</button>
```

**Warum nicht Flask:**
- Kein eingebauter Async-Support (müsste Quart verwenden)
- OpenAPI-Docs müssten manuell erstellt werden
- Mehr Boilerplate für REST-API

**Warum nicht Django:**
- Zu schwer für Use-Case (ORM, Admin-Panel nicht nötig)
- Längere Startzeit (wichtig für Embedded-System)
- Komplexere Konfiguration

**Authentication-Strategie:**

**Phase 1 (Initial):**
```python
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

@app.get("/admin")
async def admin_panel(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, os.getenv("WEB_PASSWORD"))
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401)
    return templates.TemplateResponse("admin.html", {"request": request})
```

**Phase 2 (Später):**
- JWT Tokens mit `python-jose`
- Session-basierte Auth
- Optional: OAuth2 (für Multi-User)

---

## 17. Frontend-Library: htmx

**Entscheidung:** htmx statt React/Vue/Vanilla JS

**Begründung:**
- **Kein Build-Prozess:** Direktes HTML + `<script src="htmx.min.js">`
- **Server-Side-Rendering:** SEO-freundlich, schnelles Initial-Load
- **Weniger Komplexität:** Kein npm, webpack, babel, etc.
- **Progressives Enhancement:** Funktioniert auch ohne JavaScript
- **Kleine Größe:** ~14KB minified+gzipped

**Alternativen erwogen:**

**React/Vue:**
- ❌ Build-Prozess notwendig (npm, webpack)
- ❌ Mehr Komplexität für einfachen Admin-UI
- ❌ Größerer Download (~40KB+ gzipped)
- ✅ Bessere Component-Architektur (nicht nötig hier)

**Vanilla JavaScript:**
- ✅ Kein Framework nötig
- ❌ Mehr Boilerplate für AJAX-Requests
- ❌ Manuelles DOM-Management

**Alpine.js:**
- ✅ Sehr klein (~15KB)
- ✅ Reaktive Daten-Binding
- ⚖️ Kombinierbar mit htmx (für komplexere Interaktionen)

**Entscheidung:** htmx als Basis, Alpine.js optional für komplexe UI-Komponenten

---

## Zusammenfassung: Tech-Stack

```
┌─────────────────────────────────────────┐
│         User Interaction                │
│  (GPIO-Button, CalDAV-Kalender, Web-UI) │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Python Orchestrator (main.py)         │
│   - Event Loop (asyncio)                │
│   - Meeting Manager                     │
│   - GPIO Handler (gpiozero)             │
│   - Calendar Sync (caldav)              │
│   - FastAPI Web Server                  │
└──┬────────┬─────────┬────────┬──────┬───┘
   │        │         │        │      │
   │        │         │        │      │
   ▼        ▼         ▼        ▼      ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ ┌────────┐
│ GPIO │ │CalDAV│ │Playwright│PulseAudio│Web    │
│Buttons│ │Server│ │(Browser)││(Audio)   │Browser│
│ LEDs │ │      │ │        ││          │(Admin)│
└──────┘ └──────┘ └───┬────┘└────┬─────┘────┘
                      │          │
                      ▼          ▼
               ┌────────────┐ ┌─────────┐
               │  Chromium  │ │Speakerphone│
               │  (Kiosk)   │ │Webcam   │
               └─────┬──────┘ └────┬────┘
                     │             │
                     ▼             ▼
               ┌──────────────────────┐
               │  BigBlueButton       │
               │  Server (extern)     │
               └──────────────────────┘
```

**Sprachen:** Python (Orchestrator + Web), Bash (Scripts), YAML (Config), HTML/CSS/JS (Web-UI)
**Frameworks:** FastAPI (Web), Playwright (Browser), gpiozero (GPIO), caldav (Kalender), htmx (Frontend)
**Services:** systemd, PulseAudio, Chromium, Xorg
**Infrastruktur:** Raspberry Pi 4, BigBlueButton-Server (extern), CalDAV-Server (extern/lokal)

---

**Letzte Aktualisierung:** 2025-11-15
**Änderungen:** Web-Admin-Interface (FastAPI + htmx) hinzugefügt
**Nächste Review:** Nach Phase 7 Implementation (Web-UI fertig)
