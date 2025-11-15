# Raspberry Pi Test-Anleitung

**RaspberryMeet - BigBlueButton Automation testen**

Diese Anleitung beschreibt, wie Sie den aktuellen Entwicklungsstand auf einem Raspberry Pi 4 testen können.

---

## Voraussetzungen

### Hardware
- **Raspberry Pi 4** (2GB+ RAM empfohlen, 4GB ideal)
- **SD-Karte** mit Raspberry Pi OS (Bullseye oder neuer)
- **HDMI-Monitor** (um den Browser zu sehen)
- **Internetverbindung** (Ethernet oder WiFi)
- Optional: USB-Webcam und Konferenz-Freisprecheinrichtung

### Software
- **Raspberry Pi OS** (64-bit empfohlen für bessere Performance)
- **Python 3.11+** (sollte vorinstalliert sein)
- **Git** (sollte vorinstalliert sein)

---

## Schritt 1: Raspberry Pi vorbereiten

### 1.1 System aktualisieren

Öffnen Sie ein Terminal auf dem Raspberry Pi und führen Sie aus:

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Benötigte System-Pakete installieren

```bash
# Python-Entwicklungspakete
sudo apt install -y python3-pip python3-venv python3-dev

# Git (falls nicht vorhanden)
sudo apt install -y git

# Playwright-Abhängigkeiten für Chromium
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

---

## Schritt 2: Repository klonen

### 2.1 Arbeitsverzeichnis erstellen

```bash
cd ~
mkdir -p projects
cd projects
```

### 2.2 Repository klonen

```bash
git clone https://github.com/Sico93/RaspberryMeet.git
cd RaspberryMeet
```

### 2.3 Auf den richtigen Branch wechseln

```bash
# Den aktuellen Entwicklungsbranch auschecken
git checkout claude/claude-md-mi0ls28jefrj31gk-01Fy51p4K9pYPy9KWyM2Uw6R
```

---

## Schritt 3: Python Virtual Environment einrichten

### 3.1 Virtual Environment erstellen

```bash
python3 -m venv venv
```

### 3.2 Virtual Environment aktivieren

```bash
source venv/bin/activate
```

Sie sollten jetzt `(venv)` vor Ihrem Terminal-Prompt sehen.

### 3.3 pip aktualisieren

```bash
pip install --upgrade pip
```

---

## Schritt 4: Python-Abhängigkeiten installieren

### 4.1 Requirements installieren

```bash
pip install -r requirements.txt
```

**Hinweis:** Dies kann 5-10 Minuten dauern auf einem Raspberry Pi.

### 4.2 Playwright-Browser installieren

```bash
playwright install chromium
```

**Wichtig:** Dies lädt Chromium herunter (~300 MB). Stellen Sie sicher, dass genug Platz auf der SD-Karte ist.

### 4.3 Installation überprüfen

```bash
python -c "import playwright; print('Playwright installed:', playwright.__version__)"
```

Sollte ausgeben: `Playwright installed: 1.41.0` (oder ähnlich)

---

## Schritt 5: Konfiguration erstellen

### 5.1 .env-Datei aus Vorlage erstellen

```bash
cp .env.example .env
```

### 5.2 .env-Datei bearbeiten

Öffnen Sie die `.env`-Datei mit einem Editor:

```bash
nano .env
```

**Mindestens diese Zeile anpassen:**

```bash
BBB_DEFAULT_ROOM_URL=https://ihre-bbb-server.de/b/raum-name
```

Ersetzen Sie die URL durch Ihren tatsächlichen BigBlueButton-Raum.

**Optional (falls Ihr Raum ein Passwort hat):**

```bash
BBB_DEFAULT_ROOM_PASSWORD=ihr-raum-passwort
```

**Optional (Benutzername ändern):**

```bash
BBB_DEFAULT_USERNAME=RaspberryPi-Test
```

Speichern mit `Ctrl+O`, Enter, dann `Ctrl+X` zum Beenden.

---

## Schritt 6: Demo ausführen

### 6.1 Einfacher Demo-Test (empfohlen)

```bash
python demo_bbb_join.py
```

**Was passiert:**
1. Ein Chromium-Fenster öffnet sich
2. Der Browser navigiert zu Ihrem BBB-Raum
3. Automatische Anmeldung mit Benutzername
4. Automatisches Klicken auf "Beitreten"
5. Automatisches Aktivieren des Mikrofons
6. 60 Sekunden im Meeting bleiben
7. Automatisches Verlassen des Meetings
8. Browser schließt sich

### 6.2 Ausführlicher Test mit Debug-Logs

```bash
python tests/manual/test_bbb_join.py
```

Dies zeigt detaillierte Logs über jeden Schritt.

### 6.3 Demo vorzeitig beenden

Drücken Sie `Ctrl+C` im Terminal, um die Demo zu beenden.

---

## Schritt 7: Testen mit verschiedenen Modi

### 7.1 Headless-Modus testen (ohne sichtbaren Browser)

Bearbeiten Sie `demo_bbb_join.py`:

```bash
nano demo_bbb_join.py
```

Ändern Sie Zeile ~28:

```python
async with BrowserController(
    bbb_config=config.bbb,
    headless=True,  # <- Ändern Sie False zu True
    kiosk_mode=False,
) as browser:
```

Speichern und ausführen:

```bash
python demo_bbb_join.py
```

Jetzt läuft der Browser unsichtbar im Hintergrund.

### 7.2 Kiosk-Modus testen (Vollbild)

Ändern Sie beide Flags:

```python
    headless=False,
    kiosk_mode=True,  # <- Ändern Sie False zu True
```

Der Browser startet im Vollbildmodus ohne Adressleiste.

---

## Fehlerbehebung

### Problem: "playwright: command not found"

**Lösung:**
```bash
# Sicherstellen, dass venv aktiviert ist
source venv/bin/activate

# Playwright nochmal installieren
pip install playwright
playwright install chromium
```

### Problem: "BBB_DEFAULT_ROOM_URL not configured"

**Lösung:**
```bash
# .env-Datei prüfen
cat .env | grep BBB_DEFAULT_ROOM_URL

# Falls leer, mit nano bearbeiten:
nano .env
```

### Problem: Browser startet nicht / schwarzer Bildschirm

**Lösung:**
```bash
# X11-Display prüfen
echo $DISPLAY

# Falls leer:
export DISPLAY=:0

# Demo nochmal starten
python demo_bbb_join.py
```

### Problem: "Module not found" Fehler

**Lösung:**
```bash
# Prüfen ob venv aktiviert ist
which python
# Sollte zeigen: /home/pi/projects/RaspberryMeet/venv/bin/python

# Falls nicht, aktivieren:
source venv/bin/activate

# Requirements nochmal installieren:
pip install -r requirements.txt
```

### Problem: Playwright-Browser fehlen

**Lösung:**
```bash
# System-Abhängigkeiten installieren
sudo apt install -y libnss3 libnspr4 libdbus-1-3 libatk1.0-0

# Browser nochmal installieren
playwright install chromium
playwright install-deps chromium
```

### Problem: Zu wenig RAM

**Symptom:** Browser crasht oder System wird sehr langsam

**Lösung:**
```bash
# Swap-Speicher erhöhen
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 setzen (statt 100)
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## Performance-Tipps für Raspberry Pi

### 1. GPU-Speicher erhöhen (für bessere Browser-Performance)

```bash
sudo raspi-config
# Performance Options -> GPU Memory -> 256 MB einstellen
sudo reboot
```

### 2. Chromium-Flags optimieren

Die `browser_controller.py` nutzt bereits optimierte Flags:
- `--disable-dev-shm-usage` (weniger RAM-Nutzung)
- `--no-default-browser-check`
- `--disable-infobars`

### 3. Headless-Modus für Tests nutzen

Headless-Modus spart ca. 30% RAM:

```python
headless=True
```

---

## Erfolgskriterien

✅ **Test erfolgreich, wenn:**
- Browser öffnet sich automatisch
- BBB-Raum wird geladen
- Automatische Anmeldung funktioniert
- Sie sehen sich selbst im Meeting
- Nach 60 Sekunden wird automatisch verlassen
- Keine Python-Fehler im Terminal

❌ **Test fehlgeschlagen, wenn:**
- Browser crasht
- Login-Felder werden nicht ausgefüllt
- Python-Exceptions im Terminal
- Browser hängt bei einem Schritt

---

## Logs überprüfen

Wenn etwas nicht funktioniert, schauen Sie sich die Logs an:

```bash
# Demo nochmal mit erhöhtem Log-Level ausführen
# Bearbeiten Sie demo_bbb_join.py und ändern Sie:
logger = setup_logger("demo", level="DEBUG")  # statt INFO
```

---

## Nächste Schritte nach erfolgreichem Test

Wenn der Test erfolgreich war, können Sie:

1. **GPIO-Buttons testen** (sobald implementiert)
2. **CalDAV-Integration testen** (sobald implementiert)
3. **Web-Interface testen** (sobald implementiert)
4. **Auto-Start beim Booten einrichten**

---

## Support

Bei Problemen:
1. Prüfen Sie die Fehlermeldungen im Terminal
2. Schauen Sie in `TROUBLESHOOTING.md` (wird noch erstellt)
3. Erstellen Sie ein GitHub Issue mit:
   - Raspberry Pi Modell
   - Raspberry Pi OS Version (`cat /etc/os-release`)
   - Python Version (`python --version`)
   - Komplette Fehlermeldung
   - Inhalt der .env-Datei (ohne Passwörter!)

---

## Deaktivierung nach Test

Nach dem Test können Sie das Virtual Environment deaktivieren:

```bash
deactivate
```

Zum erneuten Aktivieren:

```bash
cd ~/projects/RaspberryMeet
source venv/bin/activate
```

---

**Viel Erfolg beim Testen! 🎉**
