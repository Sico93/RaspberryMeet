# RaspberryMeet Scripts

Utility-Scripts für Setup und Verwaltung.

## 📜 Verfügbare Scripts

### `hash_password.py`

Generiert SHA-256 Hashes für Web-Interface-Passwörter.

**Verwendung:**

```bash
# Interaktiv (empfohlen - sicherer)
python scripts/hash_password.py

# Mit Passwort als Argument (unsicherer, sichtbar in History)
python scripts/hash_password.py mein-passwort
```

**Ausgabe:**

```
🔐 RaspberryMeet Password Hash Generator
========================================================

Enter the password you want to hash:
Password: ****
Confirm password: ****

✅ Password hashed successfully!

------------------------------------------------------------
Add this line to your .env file:
------------------------------------------------------------

WEB_PASSWORD=sha256:abc123def456789...

------------------------------------------------------------
```

**Verwendung des Hashes:**

1. Kopieren Sie den generierten Hash (inklusive `sha256:` Prefix)
2. Fügen Sie ihn in Ihre `.env` Datei ein:
   ```bash
   WEB_PASSWORD=sha256:abc123def456789...
   ```
3. Starten Sie den Web-Server neu

**Sicherheitshinweise:**

- ✅ Verwenden Sie die interaktive Eingabe (ohne Argument)
- ✅ Der Hash beginnt immer mit `sha256:`
- ✅ Klartext-Passwörter funktionieren weiterhin (mit Warnung)
- ⚠️ Passwörter als Argument können in der Shell-History erscheinen

---

### `test_gpio.py`

Testet GPIO-Hardware (Buttons und LEDs) ohne Browser-Integration.

**Verwendung:**

```bash
python scripts/test_gpio.py
```

**Was wird getestet:**
1. LED-Zustände (alle Farben durchlaufen)
2. Button-Erkennung (drücken und LED-Wechsel beobachten)

**Ausgabe:**
```
🔧 GPIO Hardware Test
========================================================

=== Testing LED States ===

Setting LED: Off (both LEDs off)
Setting LED: Green (ready)
Setting LED: Red (in meeting)
...

=== Testing Button ===
Press the button on GPIO 17...
🔘 Button pressed! (Count: 1)
   → Setting LED to RED
```

---

### `install_services.sh`

Installiert systemd-Services für Autostart beim Booten.

**Verwendung:**

```bash
sudo ./scripts/install_services.sh
```

**Features:**
- Interaktive Auswahl der zu installierenden Services
- Automatische Pfad-Anpassung
- Benutzer-Berechtigungen konfigurieren (GPIO, Video)
- Services aktivieren und optional starten

**Services:**
1. `raspberrymeet.service` - Haupt-Orchestrator (GPIO + Browser)
2. `raspberrymeet-web.service` - Web Admin Interface
3. `raspberrymeet-kiosk.service` - Kiosk Display (Vollbild)

**Interaktiver Dialog:**
```
Select Services to Install
========================================

Available services:
  1) raspberrymeet.service       - Main orchestrator
  2) raspberrymeet-web.service   - Web admin interface
  3) raspberrymeet-kiosk.service - Kiosk display
  4) All services

Enter your choice (1-4): 4
```

---

### `manage_services.sh`

Verwaltet RaspberryMeet systemd-Services.

**Verwendung:**

```bash
# Interaktiver Modus
sudo ./scripts/manage_services.sh

# Command-Line-Modus
sudo ./scripts/manage_services.sh status
sudo ./scripts/manage_services.sh start
sudo ./scripts/manage_services.sh stop
sudo ./scripts/manage_services.sh restart
sudo ./scripts/manage_services.sh logs
```

**Features:**
- Status-Übersicht aller Services
- Services starten/stoppen/neu starten
- Autostart aktivieren/deaktivieren
- Live-Logs anzeigen

**Beispiel-Ausgabe:**
```
RaspberryMeet Services Status
────────────────────────────────────────────────────────
Orchestrator (GPIO + Browser)      Running
Web Interface                      Running
Kiosk Display                      Stopped (Disabled)
```

---

### `setup_audio.sh`

Konfiguriert PulseAudio für optimale Audio-Qualität mit Konferenz-Freisprecheinrichtungen.

**Verwendung:**

```bash
./scripts/setup_audio.sh
```

**Features:**
- Interaktive Menü-Führung
- Audio-Eingabegeräte (Mikrofone) auflisten
- Audio-Ausgabegeräte (Lautsprecher) auflisten
- Default-Devices manuell setzen
- Audio-Tests (Aufnahme/Wiedergabe)
- Netzwerk-Audio-Konfiguration (optional)

**Menü-Optionen:**
```
Audio/Video Setup Menu
========================================
  1) List audio input devices (microphones)
  2) List audio output devices (speakers)
  3) Set default input device
  4) Set default output device
  5) Test speakers
  6) Test microphone
  7) Show video devices
  8) Configure network audio (advanced)
  9) Exit
```

---

### `pair_bluetooth.sh`

Wizard für Pairing von Bluetooth-Konferenz-Freisprecheinrichtungen.

**Verwendung:**

```bash
./scripts/pair_bluetooth.sh
```

**Features:**
- Auto-Pair Wizard (empfohlener Flow)
- Device-Scanning mit bluetoothctl
- Trust/Pair/Connect-Sequenz
- PulseAudio-Modul-Laden
- Verbindungs-Status anzeigen
- Connect/Disconnect/Remove-Operationen

**Auto-Pair Flow:**
```
Bluetooth Pairing Menu
========================================
  1) Auto-pair wizard (recommended)
  2) Show paired devices
  3) Connect to device
  4) Disconnect device
  5) Remove device
  6) Scan for devices
  7) Exit
```

---

### `test_audio_video.py`

Testet Audio- und Video-Hardware umfassend.

**Verwendung:**

```bash
python scripts/test_audio_video.py
```

**Was wird getestet:**
1. PulseAudio-Verfügbarkeit
2. Audio-Eingabegeräte (Mikrofone)
3. Audio-Ausgabegeräte (Lautsprecher)
4. Video-Geräte (Webcams)
5. Bevorzugte Konferenz-Geräte (Jabra, Anker, eMeet, etc.)
6. Default-Device-Konfiguration
7. Auto-Konfiguration

**Ausgabe:**
```
🧪 RaspberryMeet Audio/Video Hardware Test
====================================================================

🎤 Audio Device Test
====================================================================
✅ PulseAudio is available

Audio Input Devices (Microphones):
--------------------------------------------------------------------
  ✓ Jabra Speak 510 [DEFAULT]
    Built-in Audio Analog Stereo

Audio Output Devices (Speakers):
--------------------------------------------------------------------
  ✓ Jabra Speak 510 [DEFAULT]
    HDMI Audio

📹 Video Device Test
====================================================================
Found 1 webcam(s):
  1. Logitech HD Pro Webcam C920
     Device: /dev/video0

✅ Video devices detected successfully
```

---

## Weitere Scripts (geplant)

- `install.sh` - Automatische Installation und Setup
- `setup_display.sh` - X11/Kiosk-Modus-Setup
- `update.sh` - Update-Deployment

---

**Hinweis:** Alle Scripts sind im Repository dokumentiert und sicher zu verwenden.
