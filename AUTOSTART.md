# Autostart Setup - RaspberryMeet

**Systemd-Services für automatischen Start beim Booten**

Dieses Dokument beschreibt, wie Sie RaspberryMeet so einrichten, dass es automatisch beim Hochfahren des Raspberry Pi startet.

---

## 📋 Übersicht

RaspberryMeet bietet drei systemd-Services:

| Service | Beschreibung | Empfohlen für |
|---------|--------------|---------------|
| `raspberrymeet.service` | Haupt-Orchestrator (GPIO + Browser) | **Alle Setups** |
| `raspberrymeet-web.service` | Web Admin Interface | Web-Fernsteuerung |
| `raspberrymeet-kiosk.service` | Kiosk-Display (Browser im Vollbild) | Dedicated Display-Setup |

**Empfohlene Konfigurationen:**

- **Standard (GPIO-Button):** Nur `raspberrymeet.service`
- **Mit Web-Interface:** `raspberrymeet.service` + `raspberrymeet-web.service`
- **Kiosk-Modus:** Alle drei Services

---

## 🚀 Schnell-Installation

### Option 1: Automatisches Installations-Script (Empfohlen)

```bash
# Als root ausführen
sudo ./scripts/install_services.sh
```

Das Script:
1. Konfiguriert Benutzer-Berechtigungen (GPIO, Video)
2. Fragt, welche Services installiert werden sollen
3. Installiert und aktiviert die Services
4. Bietet an, Services sofort zu starten

### Option 2: Manuelle Installation

Siehe Abschnitt "Manuelle Installation" weiter unten.

---

## 🎯 Automatisches Installations-Script

### Verwendung

```bash
cd /home/pi/RaspberryMeet
sudo ./scripts/install_services.sh
```

### Interaktiver Dialog

```
========================================
Select Services to Install
========================================

Available services:
  1) raspberrymeet.service       - Main orchestrator (GPIO + Browser)
  2) raspberrymeet-web.service   - Web admin interface
  3) raspberrymeet-kiosk.service - Kiosk display (optional)
  4) All services

Enter your choice (1-4): 4

...

Start services now? (y/n): y
```

### Was macht das Script?

1. **Berechtigungen setzen:**
   - Fügt User zur `gpio`-Gruppe hinzu (GPIO-Zugriff)
   - Fügt User zur `video`-Gruppe hinzu (Kamera-Zugriff)

2. **Services installieren:**
   - Kopiert Service-Dateien nach `/etc/systemd/system/`
   - Passt Pfade automatisch an
   - Setzt korrekten User/Group

3. **Services aktivieren:**
   - `systemctl daemon-reload`
   - `systemctl enable <service>`

4. **Services starten** (optional):
   - `systemctl start <service>`

---

## 🛠️ Service-Management

### Mit Management-Script (Einfach)

```bash
# Interaktiver Modus
sudo ./scripts/manage_services.sh

# Command-Line-Modus
sudo ./scripts/manage_services.sh status    # Status anzeigen
sudo ./scripts/manage_services.sh start     # Alle starten
sudo ./scripts/manage_services.sh stop      # Alle stoppen
sudo ./scripts/manage_services.sh restart   # Alle neu starten
sudo ./scripts/manage_services.sh logs      # Logs anzeigen
```

### Manuelle systemctl-Befehle

**Status prüfen:**
```bash
sudo systemctl status raspberrymeet.service
sudo systemctl status raspberrymeet-web.service
sudo systemctl status raspberrymeet-kiosk.service
```

**Service starten:**
```bash
sudo systemctl start raspberrymeet.service
```

**Service stoppen:**
```bash
sudo systemctl stop raspberrymeet.service
```

**Service neu starten:**
```bash
sudo systemctl restart raspberrymeet.service
```

**Autostart aktivieren:**
```bash
sudo systemctl enable raspberrymeet.service
```

**Autostart deaktivieren:**
```bash
sudo systemctl disable raspberrymeet.service
```

---

## 📊 Logs anzeigen

### Mit Management-Script

```bash
sudo ./scripts/manage_services.sh logs
```

Wählen Sie dann den Service aus.

### Direkt mit journalctl

**Live-Logs verfolgen:**
```bash
sudo journalctl -u raspberrymeet.service -f
```

**Letzte 100 Zeilen:**
```bash
sudo journalctl -u raspberrymeet.service -n 100
```

**Nur Fehler:**
```bash
sudo journalctl -u raspberrymeet.service -p err
```

**Seit heute:**
```bash
sudo journalctl -u raspberrymeet.service --since today
```

**Seit 1 Stunde:**
```bash
sudo journalctl -u raspberrymeet.service --since "1 hour ago"
```

---

## 📝 Manuelle Installation

Falls Sie das Installations-Script nicht verwenden möchten:

### Schritt 1: Benutzer-Berechtigungen

```bash
# GPIO-Zugriff
sudo usermod -a -G gpio pi

# Video-Zugriff (Kamera)
sudo usermod -a -G video pi

# Neu anmelden oder:
newgrp gpio
```

### Schritt 2: Service-Dateien kopieren

```bash
# Orchestrator-Service
sudo cp systemd/raspberrymeet.service /etc/systemd/system/

# Web-Interface-Service
sudo cp systemd/raspberrymeet-web.service /etc/systemd/system/

# Kiosk-Service (optional)
sudo cp systemd/raspberrymeet-kiosk.service /etc/systemd/system/
```

### Schritt 3: Pfade anpassen (falls Installation nicht in /home/pi/RaspberryMeet)

```bash
# Service-Datei bearbeiten
sudo nano /etc/systemd/system/raspberrymeet.service

# Ändern Sie:
# WorkingDirectory=/home/pi/RaspberryMeet
# EnvironmentFile=/home/pi/RaspberryMeet/.env
# ExecStart=/home/pi/RaspberryMeet/venv/bin/python ...

# Zu Ihrem tatsächlichen Pfad
```

### Schritt 4: Services aktivieren

```bash
# Daemon neu laden
sudo systemctl daemon-reload

# Services aktivieren
sudo systemctl enable raspberrymeet.service
sudo systemctl enable raspberrymeet-web.service
# sudo systemctl enable raspberrymeet-kiosk.service  # Optional
```

### Schritt 5: Services starten

```bash
sudo systemctl start raspberrymeet.service
sudo systemctl start raspberrymeet-web.service
```

---

## 🔧 Konfiguration

### Umgebungsvariablen (.env)

Die Services laden Konfiguration aus `.env`:

```bash
# Pfad in Service-Datei:
EnvironmentFile=/home/pi/RaspberryMeet/.env
```

**Wichtige Einstellungen:**

```bash
# Auto-Join beim Boot
AUTO_JOIN_ON_BOOT=true  # Automatisch Meeting beitreten

# GPIO aktivieren
GPIO_ENABLED=true

# Web-Interface
WEB_ENABLED=true
WEB_PORT=8080

# Kiosk-Modus
KIOSK_MODE=true
```

### Service-Optionen

#### Resource Limits

In den Service-Dateien sind Resource-Limits definiert:

```ini
# Speicher-Limit
MemoryMax=1G         # Orchestrator
MemoryMax=512M       # Web-Interface

# CPU-Limit
CPUQuota=80%         # Orchestrator
CPUQuota=50%         # Web-Interface
```

#### Restart-Policy

```ini
Restart=always       # Automatischer Neustart bei Absturz
RestartSec=10        # 10 Sekunden warten vor Neustart
```

---

## 🎮 Verschiedene Nutzungsszenarien

### Szenario 1: Nur GPIO-Button (Headless)

**Services:**
- ✅ `raspberrymeet.service`

**Konfiguration (.env):**
```bash
GPIO_ENABLED=true
AUTO_JOIN_ON_BOOT=false   # Manueller Start per Button
KIOSK_MODE=false          # Kein Display
```

**Verwendung:**
- Button drücken → Meeting beitreten
- Browser läuft headless im Hintergrund

### Szenario 2: Mit Web-Interface

**Services:**
- ✅ `raspberrymeet.service`
- ✅ `raspberrymeet-web.service`

**Konfiguration (.env):**
```bash
GPIO_ENABLED=true
WEB_ENABLED=true
WEB_PORT=8080
```

**Verwendung:**
- Button ODER Web-Interface nutzen
- Status über http://raspberrypi.local:8080 prüfen

### Szenario 3: Kiosk mit Display

**Services:**
- ✅ `raspberrymeet.service`
- ✅ `raspberrymeet-web.service`
- ✅ `raspberrymeet-kiosk.service`

**Konfiguration (.env):**
```bash
KIOSK_MODE=true
AUTO_JOIN_ON_BOOT=true   # Automatisch beim Boot beitreten
```

**Verwendung:**
- Display zeigt Web-Interface im Vollbild
- Automatischer Meeting-Join beim Start
- Button für Leave/Re-Join

### Szenario 4: Auto-Join beim Boot

**Services:**
- ✅ `raspberrymeet.service`

**Konfiguration (.env):**
```bash
AUTO_JOIN_ON_BOOT=true
BBB_DEFAULT_ROOM_URL=https://bbb.example.eu/b/raum
```

**Verwendung:**
- Pi hochfahren → automatisch im Meeting
- Kein Button-Druck nötig
- Ideal für feste Installationen

---

## 🔍 Troubleshooting

### Service startet nicht

**Symptom:** `systemctl status` zeigt "failed" oder "inactive"

**Lösung:**
```bash
# Logs prüfen
sudo journalctl -u raspberrymeet.service -n 50

# Häufige Fehler:
# - .env-Datei nicht gefunden → Pfad in Service-Datei prüfen
# - Python-Abhängigkeiten fehlen → pip install -r requirements.txt
# - Berechtigungen fehlen → User zu gpio-Gruppe hinzufügen
```

### Service startet, aber Meeting-Join schlägt fehl

**Symptom:** LED blinkt rot, Logs zeigen Fehler

**Lösung:**
```bash
# BBB-Konfiguration prüfen
grep BBB_ /home/pi/RaspberryMeet/.env

# Browser-Automation testen
cd /home/pi/RaspberryMeet
source venv/bin/activate
python demo_bbb_join.py
```

### GPIO funktioniert nicht

**Symptom:** Button-Drücke werden nicht erkannt

**Lösung:**
```bash
# Berechtigungen prüfen
groups pi  # Sollte "gpio" enthalten

# Falls nicht:
sudo usermod -a -G gpio pi
sudo reboot  # Neustart erforderlich!

# GPIO-Test
python scripts/test_gpio.py
```

### Web-Interface nicht erreichbar

**Symptom:** http://raspberrypi.local:8080 lädt nicht

**Lösung:**
```bash
# Web-Service-Status prüfen
sudo systemctl status raspberrymeet-web.service

# Port prüfen
sudo netstat -tulpn | grep 8080

# Firewall prüfen
sudo ufw status  # Falls aktiviert
```

### Service verbraucht zu viel RAM

**Symptom:** System wird langsam, Out-of-Memory

**Lösung:**
```bash
# Memory-Limit anpassen
sudo nano /etc/systemd/system/raspberrymeet.service

# Ändern:
MemoryMax=512M  # Von 1G auf 512M reduzieren

# Reload
sudo systemctl daemon-reload
sudo systemctl restart raspberrymeet.service
```

### Logs zu groß

**Symptom:** Festplatte voll durch Logs

**Lösung:**
```bash
# Journal-Größe begrenzen
sudo nano /etc/systemd/journald.conf

# Hinzufügen:
SystemMaxUse=100M

# Journald neu starten
sudo systemctl restart systemd-journald

# Alte Logs löschen
sudo journalctl --vacuum-size=50M
```

---

## 🔄 Updates und Wartung

### Service nach Code-Update neu starten

```bash
cd /home/pi/RaspberryMeet

# Code aktualisieren
git pull

# Dependencies aktualisieren
source venv/bin/activate
pip install -r requirements.txt

# Services neu starten
sudo systemctl restart raspberrymeet.service
sudo systemctl restart raspberrymeet-web.service
```

### Service-Dateien aktualisieren

```bash
# Nach Änderungen an systemd/*.service
sudo cp systemd/raspberrymeet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart raspberrymeet.service
```

---

## 🗑️ Deinstallation

### Services entfernen

```bash
# Services stoppen
sudo systemctl stop raspberrymeet.service
sudo systemctl stop raspberrymeet-web.service
sudo systemctl stop raspberrymeet-kiosk.service

# Services deaktivieren
sudo systemctl disable raspberrymeet.service
sudo systemctl disable raspberrymeet-web.service
sudo systemctl disable raspberrymeet-kiosk.service

# Service-Dateien löschen
sudo rm /etc/systemd/system/raspberrymeet*.service

# Daemon neu laden
sudo systemctl daemon-reload
```

---

## 📚 Weitere Ressourcen

- **Systemd Documentation:** https://www.freedesktop.org/software/systemd/man/
- **Journalctl Guide:** https://www.digitalocean.com/community/tutorials/how-to-use-journalctl-to-view-and-manipulate-systemd-logs

---

**Version:** 1.0
**Letzte Aktualisierung:** 2025-11-15
