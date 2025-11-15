# RaspberryMeet - Implementierungsplan

**Erstellt:** 2025-11-15
**Projekt:** BigBlueButton Kiosk Client für Raspberry Pi 4
**Ziel:** Einfacher Meeting-Zugang per Knopfdruck ohne Tastatur/Maus

---

## Executive Summary

**Was wird gebaut:**
Ein Raspberry Pi 4 System, das per GPIO-Button oder automatisch über Kalendereinladungen BigBlueButton-Meetings beitritt. Bedienung vollständig ohne Tastatur/Maus für Standardszenarien.

**Kernfunktionen:**
1. **GPIO-Button → Standard-Meeting:** Ein Knopfdruck = sofortiger Beitritt zum konfigurierten BBB-Raum
2. **Kalender-Integration:** Automatisches Beitreten zu Meetings basierend auf CalDAV-Einladungen
3. **Web-Admin-Interface:** Lokale Web-UI für Meeting-Steuerung und Konfiguration aus dem Netzwerk
4. **Hardware-Optimiert:** Konferenzspinne als Standard-Audio, USB-Webcam automatisch erkannt
5. **Privacy-First:** Nur Open Source, EU-gehostete Services, keine USA/China-Dienste

**Technologie-Stack:**
- **Browser:** Chromium im Kiosk-Modus (Vollbild, keine UI)
- **Automatisierung:** Python + Playwright/Selenium für Browser-Steuerung
- **Web-Backend:** FastAPI für REST API und Web-Interface
- **Hardware:** gpiozero für GPIO-Buttons und LEDs
- **Kalender:** CalDAV-Client (Nextcloud/Radicale kompatibel)
- **Audio:** PulseAudio mit automatischer Speakerphone-Erkennung
- **System:** systemd Services für Auto-Start

---

## Projektphasen

### Phase 1: Foundation & Prototyping (Woche 1-2)
**Ziel:** Grundlegende Infrastruktur und manuelle BBB-Verbindung

#### 1.1 Entwicklungsumgebung
- [ ] Python 3.11+ Installation und venv Setup
- [ ] Git Repository Struktur nach CLAUDE.md erstellen
- [ ] requirements.txt mit initialen Dependencies
- [ ] .gitignore für Python, Secrets, IDE-Dateien
- [ ] .env.example Template erstellen

#### 1.2 BBB-Verbindungstest (Manuell)
- [ ] BBB-Server URL und API-Zugangsdaten erhalten
- [ ] Test-Raum auf BBB-Server erstellen
- [ ] Chromium auf Raspberry Pi OS installieren
- [ ] Manueller BBB-Zugang über Chromium testen
- [ ] Audio/Video-Geräte in BBB verifizieren

#### 1.3 Browser-Automatisierung Proof-of-Concept
- [ ] Playwright Installation und Setup
- [ ] Script für automatischen BBB-Login (Python)
- [ ] Automatisches Ausfüllen von Benutzername
- [ ] Automatisches Klicken auf "Join Audio"
- [ ] Fehlerbehandlung für Verbindungsprobleme

**Deliverables:**
- Funktionierender Prototyp: `python join_meeting.py` startet BBB-Meeting automatisch
- Dokumentation der BBB-Selektoren und Automationsschritte

---

### Phase 2: GPIO Hardware Integration (Woche 2-3)
**Ziel:** Physische Buttons steuern Meeting-Beitritt

#### 2.1 GPIO-Setup
- [ ] gpiozero Library installieren
- [ ] GPIO-Pin-Belegung definieren (z.B. GPIO17 = Join Button)
- [ ] Hardware-Schaltplan für Buttons + Pull-Down-Widerstände
- [ ] Test-Script für Button-Erkennung (LED blinkt bei Druck)

#### 2.2 Button-Event-Handler
- [ ] Button-Klick löst Meeting-Beitritt aus
- [ ] Debouncing implementieren (verhindert Mehrfachklicks)
- [ ] Long-Press vs. Short-Press Unterscheidung (optional)
- [ ] Status-LED: Grün = bereit, Rot = im Meeting, Blinken = Fehler

#### 2.3 Meeting-Orchestrator Service
- [ ] Python-Service `orchestrator/main.py` erstellen
- [ ] Event-Loop für GPIO-Überwachung
- [ ] Meeting-Status-Tracking (idle, joining, active, leaving)
- [ ] Logging-Framework (Datei + journalctl)

**Deliverables:**
- GPIO-Button startet BBB-Meeting
- LED zeigt aktuellen Status an
- Service läuft dauerhaft im Hintergrund

---

### Phase 3: Calendar Integration (Woche 3-4)
**Ziel:** Automatisches Beitreten zu geplanten Meetings

#### 3.1 CalDAV Client Implementation
- [ ] `caldav` Library installieren und testen
- [ ] Verbindung zu Test-CalDAV-Server (Nextcloud/Radicale)
- [ ] Abrufen von Kalenderevents der nächsten 24h
- [ ] Parsing von BBB-URLs aus Kalenderbeschreibungen
- [ ] Caching von Events (SQLite) für Offline-Zugriff

#### 3.2 Meeting-Scheduler
- [ ] APScheduler Integration
- [ ] Automatisches Beitreten 1 Minute vor Meeting-Start
- [ ] Automatisches Verlassen bei Meeting-Ende
- [ ] Priorisierung: Kalender-Meeting > Standard-Meeting

#### 3.3 BBB-URL-Erkennung
- [ ] Regex-Pattern für BBB-URLs in Kalendereinträgen
- [ ] Unterstützung für verschiedene BBB-URL-Formate
- [ ] Passwort-Extraktion aus Kalenderbeschreibung (optional)
- [ ] Fallback auf Standard-Meeting bei fehlender URL

**Deliverables:**
- System erkennt Kalendertermine und tritt automatisch bei
- Manuelle Tests mit Testkalender und Dummy-Meetings

---

### Phase 4: Audio/Video Device Management (Woche 4-5)
**Ziel:** Automatische Erkennung und Konfiguration von Audio/Video-Hardware

#### 4.1 PulseAudio Configuration
- [ ] PulseAudio Defaults für Konferenzspinne setzen
- [ ] Script `setup_audio.sh` für initiale Konfiguration
- [ ] Automatische Geräteerkennung bei USB-Verbindung
- [ ] Fallback auf HDMI-Audio bei fehlender Speakerphone

#### 4.2 Bluetooth-Support (Optional)
- [ ] `bluez` Installation und Konfiguration
- [ ] Pairing-Script für Bluetooth-Speakerphone
- [ ] Auto-Connect bei Boot
- [ ] Fehlerbehandlung bei Verbindungsabbruch

#### 4.3 Webcam-Konfiguration
- [ ] v4l2-utils für Kamera-Konfiguration
- [ ] Automatische Auswahl der ersten USB-Kamera
- [ ] Test-Tool: Live-Vorschau der Webcam
- [ ] Fehlerbehandlung bei fehlender Kamera

**Deliverables:**
- Konferenzspinne wird automatisch erkannt und verwendet
- Webcam funktioniert in BBB ohne manuelle Konfiguration
- Dokumentation des Audio-Setups

---

### Phase 5: Kiosk Mode & Boot Integration (Woche 5-6)
**Ziel:** System startet automatisch in BBB-Ready-Zustand

#### 5.1 X11/Wayland Kiosk Setup
- [ ] Minimal-WM Installation (openbox oder matchbox)
- [ ] Chromium Auto-Start im Kiosk-Modus
- [ ] Bildschirmschoner deaktivieren
- [ ] Auto-Login für `pi` User konfigurieren

#### 5.2 Systemd Services
- [ ] `raspberrymeet.service` für Orchestrator
- [ ] `raspberrymeet-kiosk.service` für Chromium
- [ ] Service-Dependencies korrekt definieren
- [ ] Auto-Restart bei Crashes

#### 5.3 Boot-Time Checks
- [ ] Netzwerk-Konnektivität prüfen (warte auf Internet)
- [ ] BBB-Server erreichbar? (Health Check)
- [ ] Audio-Geräte vorhanden?
- [ ] LED-Blink-Code bei Boot-Fehlern

**Deliverables:**
- Raspberry Pi bootet direkt in "Meeting-Ready" Zustand
- Chromium ist unsichtbar im Hintergrund, wartet auf Trigger
- Systemd-Logs zeigen alle Status-Informationen

---

### Phase 6: Configuration & User Experience (Woche 6-7)
**Ziel:** Einfache Konfiguration und robuste Fehlerbehandlung

#### 6.1 Configuration System
- [ ] YAML-Konfiguration für BBB-URLs, Pins, etc.
- [ ] Validierung der Config beim Start (Schema-Check)
- [ ] Beispiel-Configs für verschiedene Szenarien
- [ ] Secrets in separater .env-Datei

#### 6.2 Logging & Monitoring
- [ ] Strukturiertes Logging (JSON-Format)
- [ ] Log-Rotation konfigurieren
- [ ] Wichtige Events: Meeting-Beitritt, Fehler, GPIO-Events
- [ ] Optional: Log-Upload zu zentralem Server

#### 6.3 Error Handling & Recovery
- [ ] Retry-Logik für BBB-Verbindungsfehler
- [ ] Automatischer Browser-Neustart bei Freeze
- [ ] LED-Blink-Codes für verschiedene Fehlertypen
- [ ] "Panic Button" - GPIO-Long-Press zum System-Reset

**Deliverables:**
- `config/config.yaml` für alle Einstellungen
- Robuste Fehlerbehandlung mit automatischer Wiederherstellung
- Admin-Dokumentation für Troubleshooting

---

### Phase 7: Web Admin Interface (Woche 7)
**Ziel:** Lokales Web-Interface für Meeting-Steuerung und Konfiguration

#### 7.1 FastAPI Backend Setup
- [ ] FastAPI Installation und Basis-Setup
- [ ] REST API Endpoints für Meeting-Kontrolle
  - `GET /api/status` - Aktueller Meeting-Status
  - `POST /api/meeting/join` - Meeting beitreten (mit URL/Room-ID)
  - `POST /api/meeting/leave` - Meeting verlassen
  - `GET /api/config` - Konfiguration abrufen
  - `PUT /api/config` - Konfiguration aktualisieren
- [ ] Integration mit Meeting Manager (IPC oder Shared State)
- [ ] CORS-Konfiguration für lokales Netzwerk

#### 7.2 Frontend Implementation
- [ ] Simple HTML/CSS/JS Templates (Jinja2)
  - Dashboard: Meeting-Status, Quick-Join-Buttons
  - Meetings: Konfigurierte Räume, Kalender-Übersicht
  - Settings: BBB-URLs, CalDAV-Credentials, GPIO-Pins
  - Logs: System-Logs und Meeting-Historie
- [ ] htmx für dynamische Updates ohne Full-Reload
- [ ] Responsive Design (Desktop + Tablet/Handy)
- [ ] Deutsches UI (optional: Sprachumschaltung)

#### 7.3 Authentication & Security
- [ ] HTTP Basic Auth (initialer Schutz)
- [ ] Konfigurierbare Credentials in .env
- [ ] IP-Whitelist für vertrauenswürdige Netzwerke (optional)
- [ ] HTTPS mit selbstsigniertem Zertifikat (optional)

#### 7.4 Systemd Service Integration
- [ ] `raspberrymeet-web.service` erstellen
- [ ] Service läuft auf Port 8080 (konfigurierbar)
- [ ] Auto-Start beim Boot
- [ ] Health-Check-Endpoint für Monitoring

**Deliverables:**
- Web-Interface unter `http://raspberrypi.local:8080` erreichbar
- Meeting-Join aus Web-UI funktioniert
- Basic Auth schützt Admin-Funktionen
- Service läuft stabil im Hintergrund

---

### Phase 8: Testing & Documentation (Woche 8)
**Ziel:** Qualitätssicherung und vollständige Dokumentation

#### 8.1 Automated Testing
- [ ] Unit Tests für Meeting Manager
- [ ] Mock-Tests für GPIO (ohne Hardware)
- [ ] Integration Tests für CalDAV
- [ ] Browser-Automation Tests mit Dummy-BBB-Server

#### 8.2 Hardware Testing
- [ ] Test auf echtem Raspberry Pi 4
- [ ] Verschiedene Konferenzspinnen testen
- [ ] Bluetooth vs. USB Speakerphone
- [ ] Langzeit-Stabilitätstest (24h Dauerbetrieb)

#### 8.3 Documentation
- [ ] `docs/SETUP.md` - Vollständige Installationsanleitung
- [ ] `docs/HARDWARE.md` - GPIO-Verkabelung mit Fotos
- [ ] `docs/CALDAV_SETUP.md` - Nextcloud/Radicale Konfiguration
- [ ] `docs/USER_GUIDE.md` - Benutzerhandbuch (DE)
- [ ] `docs/TROUBLESHOOTING.md` - Häufige Probleme und Lösungen

**Deliverables:**
- 70%+ Test-Coverage
- Vollständige Dokumentation in Deutsch und Englisch
- Video-Tutorial für Installation (optional)

---

### Phase 9: Deployment & Finalisierung (Woche 9)
**Ziel:** Produktionsreifes System für Rollout

#### 9.1 Installation Script
- [ ] `scripts/install.sh` - Ein-Klick-Installation
- [ ] Automatische Dependency-Installation
- [ ] Initiale Config-Generierung (interaktiv)
- [ ] Systemd-Service-Aktivierung

#### 9.2 SD Card Image (Bonus Feature)
- [ ] Pre-configured Raspberry Pi OS Image
- [ ] Alle Dependencies vorinstalliert
- [ ] Nur Credentials müssen konfiguriert werden
- [ ] Image-Dokumentation und Checksums

#### 9.3 Security Audit
- [ ] Credentials niemals in Git
- [ ] Minimale Berechtigungen für Services
- [ ] Firewall-Regeln (nur BBB + CalDAV erreichbar)
- [ ] SSH-Härtung für Remote-Management

**Deliverables:**
- `install.sh` für einfaches Deployment
- Produktionsreife Konfiguration
- Security-Checkliste abgearbeitet

---

## Technologie-Entscheidungen

### Browser-Automatisierung: Playwright vs. Selenium

**Empfehlung: Playwright**

**Vorteile:**
- Modernere API, bessere Performance
- Nativ async/await Support (Python asyncio)
- Integrierte Auto-Waiting (weniger flaky Tests)
- Bessere Fehlerbehandlung und Screenshots

**Nachteile:**
- Etwas größer (ca. 300 MB mit Chromium)
- Weniger Community-Ressourcen als Selenium

**Fallback:** Selenium mit `undetected-chromedriver` falls Playwright Probleme macht

---

### CalDAV-Server: Empfehlung für Nutzer

**Für Einsteiger: Radicale**
- Minimal, Python-basiert (einfach zu verstehen)
- Datei-basiertes Backend (kein DB-Server nötig)
- Perfekt für Single-Room-Setup
- Installation: `pip install radicale && radicale`

**Für Organisationen: Nextcloud**
- Vollständige Groupware (Kalender, Kontakte, Dateien)
- Ausgereiftes Web-Interface
- Viele EU-Hoster verfügbar
- Mobil-Apps für einfache Terminverwaltung

**Für Puristen: Baikal**
- Nur CalDAV/CardDAV, nichts anderes
- PHP-basiert, läuft auf jedem Webserver
- Sehr stabil und wartungsarm

---

### GPIO-Pin-Belegung (Empfohlen)

```
Raspberry Pi 4 GPIO:
├── GPIO 17 (Pin 11) - Join Default Meeting Button
├── GPIO 27 (Pin 13) - Leave Meeting Button (optional)
├── GPIO 22 (Pin 15) - Mute Toggle Button (optional)
├── GPIO 23 (Pin 16) - Status LED (Grün)
├── GPIO 24 (Pin 18) - Error LED (Rot)
└── GND (Pin 6, 9, 14, 20, 25, 30, 34, 39) - Common Ground

Schaltung:
Button: GPIO Pin → Button → GND (interne Pull-Up Widerstände nutzen)
LED: GPIO Pin → LED (Anode) → 220Ω Widerstand → GND
```

---

### BBB-Automatisierung: URL-Format

**Szenario 1: Direkter Room-Join**
```
https://bbb.example.eu/b/abc-def-ghi
```
- Einfachster Fall: Direkt navigieren, Namen eingeben, Join klicken

**Szenario 2: API-generierter Join-Link**
```python
import hashlib
from urllib.parse import urlencode

def generate_bbb_join_url(server_url, meeting_id, username, password, api_secret):
    """
    Generiert einen signierten BBB-Join-Link
    """
    params = {
        'meetingID': meeting_id,
        'fullName': username,
        'password': password
    }
    query_string = urlencode(params)
    checksum = hashlib.sha1(f"join{query_string}{api_secret}".encode()).hexdigest()
    return f"{server_url}/api/join?{query_string}&checksum={checksum}"
```

**Szenario 3: Greenlight-Frontend**
```
https://bbb.example.eu/gl/abc-def-ghi
```
- Greenlight vereinfacht Raumverwaltung
- Kann direkt mit Token authentifizieren

**Empfehlung:** Starte mit Szenario 1 (am einfachsten), erweitere später zu Szenario 2 für mehr Kontrolle.

---

## Meeting-Ablauf: Sequenzdiagramm

```
User/System          Orchestrator        GPIO Handler       Browser         BBB Server
     |                    |                    |                |                |
     |--- Power On ------>|                    |                |                |
     |                    |--- Init GPIO ----->|                |                |
     |                    |--- Start Browser -->|                |                |
     |                    |                    |                |                |
     |                    |<-- Ready Signal ---|                |                |
     |                    |--- LED Green ------>|                |                |
     |                    |                    |                |                |
[Button Press]            |                    |                |                |
     |                    |<-- Button Event ---|                |                |
     |                    |--- LED Blink (joining)              |                |
     |                    |                    |                |                |
     |                    |--- Navigate to BBB URL ------------->|                |
     |                    |                    |                |--- GET room -->|
     |                    |                    |                |<-- HTML -------|
     |                    |                    |                |                |
     |                    |--- Fill Username ------------------>|                |
     |                    |--- Click Join --------------------->|                |
     |                    |                    |                |--- WebRTC ---->|
     |                    |                    |                |<-- Stream -----|
     |                    |--- LED Red (active)                 |                |
     |                    |                    |                |                |
[Meeting Ends]            |                    |                |                |
     |                    |--- Detect End ---->|                |                |
     |                    |--- Close Browser ------------------>|                |
     |                    |--- LED Green ------>|                |                |
     |                    |                    |                |                |
```

---

## Risiken und Mitigations

### Risiko 1: BBB-UI ändert sich (Browser-Selektoren brechen)
**Wahrscheinlichkeit:** Mittel
**Impact:** Hoch
**Mitigation:**
- Flexible Selektoren verwenden (mehrere Fallbacks)
- BBB-Version in Config dokumentieren
- Tests mit verschiedenen BBB-Versionen
- Plan B: BBB-API statt Browser-Automation

### Risiko 2: Netzwerk-Instabilität
**Wahrscheinlichkeit:** Mittel
**Impact:** Mittel
**Mitigation:**
- Retry-Logik mit exponential backoff
- Lokales Event-Caching (SQLite)
- LED-Indikator für Netzwerkprobleme
- Ethernet statt WiFi empfehlen

### Risiko 3: Hardware-Kompatibilität (Speakerphone)
**Wahrscheinlichkeit:** Niedrig
**Impact:** Hoch
**Mitigation:**
- Whitelist von getesteten Geräten
- Automatische Fallback-Logik (HDMI-Audio)
- Test-Script für Audio-Geräte
- Dokumentation für manuelle Konfiguration

### Risiko 4: GPIO-Button Prelleffekte
**Wahrscheinlichkeit:** Hoch
**Impact:** Niedrig
**Mitigation:**
- Software-Debouncing (gpiozero hat das built-in)
- Hardware-Debouncing (Kondensator parallel zum Button)
- Timeout zwischen Button-Events (min. 500ms)

---

## Erfolgs-Kriterien

**Minimum Viable Product (MVP) - Phase 1-6:**
- [ ] GPIO-Button startet BBB-Meeting (Standard-Raum)
- [ ] LED zeigt Meeting-Status an
- [ ] Audio/Video funktioniert automatisch
- [ ] System startet automatisch nach Boot
- [ ] Keine Tastatur/Maus nötig für Standard-Workflow

**Extended MVP (v1.0) - Phase 1-7:**
- [ ] Kalender-Integration (CalDAV)
- [ ] Web-Admin-Interface für Meeting-Steuerung
- [ ] Konfiguration über Web-UI
- [ ] Basic Auth für Web-Zugriff

**Nice-to-Have (v1.1+):**
- [ ] Mehrere Buttons für verschiedene Räume
- [ ] Bluetooth-Speakerphone-Support
- [ ] JWT-Authentifizierung für Web-UI
- [ ] Multi-Room-Support (mehrere Pis zentral verwalten)
- [ ] OTA-Updates (Over-The-Air)
- [ ] Mobile App für Meeting-Steuerung

---

## Zeitplan-Übersicht

| Woche | Phase | Hauptaktivitäten | Deliverable |
|-------|-------|------------------|-------------|
| 1-2   | Foundation | Python Setup, BBB-Test, Browser-Automation | Funktionierender Join-Script |
| 2-3   | GPIO | Hardware-Setup, Button-Events, LED-Control | Button startet Meeting |
| 3-4   | Calendar | CalDAV-Client, Scheduler, URL-Parsing | Auto-Join bei Termin |
| 4-5   | A/V | PulseAudio, Bluetooth, Webcam-Config | Hardware funktioniert |
| 5-6   | Kiosk | X11-Setup, systemd-Services, Boot-Integration | Auto-Start nach Boot |
| 6-7   | Config/UX | YAML-Config, Logging, Error-Handling | Produktionsreif |
| 7     | Web UI | FastAPI Backend, HTML/htmx Frontend, Auth | Web-Interface funktioniert |
| 8     | Testing | Unit/Integration-Tests, Hardware-Tests, Docs | 70% Coverage, Docs |
| 9     | Deploy | Install-Script, Security-Audit | Release v1.0 |
| Bonus | SD-Image | Pre-configured Pi OS Image | Flash & Go Image |

**Geschätzte Gesamtzeit:** 9 Wochen (1 Entwickler, Vollzeit) + Bonus-Phase optional
**Minimum Time-to-Demo:** 2 Wochen (nur Phase 1-2 für Proof-of-Concept)
**MVP mit Web-UI:** 7 Wochen (Phase 1-7)

---

## Nächste Schritte

### Sofort starten:
1. **Hardware besorgen:**
   - Raspberry Pi 4 (4GB+)
   - Konferenzspinne (Empfehlung: Jabra Speak 510, Anker PowerConf)
   - USB-Webcam (Logitech C920/C930e)
   - GPIO-Buttons und LEDs (siehe Hardware-Liste)

2. **BBB-Server-Zugang:**
   - BBB-Server-URL erfragen
   - API-Secret vom Administrator erhalten
   - Test-Raum mit Passwort erstellen

3. **CalDAV-Server wählen:**
   - Radicale lokal auf Laptop testen, ODER
   - Nextcloud bei EU-Hoster (z.B. Hetzner, OVH), ODER
   - Baikal auf eigenem Webspace

4. **Repository initialisieren:**
   ```bash
   cd RaspberryMeet
   mkdir -p src/orchestrator config systemd scripts tests docs hardware
   touch requirements.txt .gitignore .env.example
   git add .
   git commit -m "feat: initialize project structure"
   ```

### Für AI-Assistenten:
- **Phase 1** implementieren: `src/orchestrator/browser_controller.py` mit Playwright
- **Config-Template** erstellen: `config/config.example.yaml`
- **Install-Script** starten: `scripts/install.sh`

---

**Fragen? Unklarheiten?**
Siehe CLAUDE.md Abschnitt "Questions to Ask" für wichtige Entscheidungen, die noch zu treffen sind.

**Let's build this! 🚀**
