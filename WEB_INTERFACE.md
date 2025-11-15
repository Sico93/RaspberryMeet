# Web Admin Interface - RaspberryMeet

**FastAPI + htmx Web-Interface für Meeting-Steuerung**

Das Web Admin Interface ermöglicht die Fernsteuerung des RaspberryMeet-Systems über einen Browser im lokalen Netzwerk.

---

## Features

✅ **Meeting-Steuerung**
- Ein-Klick-Beitritt zum Standard-Meeting
- Benutzerdefinierte BBB-Raum-URLs
- Meeting verlassen
- Optionale Benutzernamen und Passwörter

✅ **Echtzeit-Status**
- Live-Status-Updates via WebSocket
- Meeting-Dauer-Anzeige
- Aktueller Raum-Anzeige
- Farbcodierte Status-Badges

✅ **Authentifizierung**
- HTTP Basic Auth
- Konfigurierbare Zugangsdaten

✅ **Responsive Design**
- Mobile-freundlich
- Sauberes, modernes UI
- Keine JavaScript-Framework-Abhängigkeiten (nur htmx)

---

## Schnellstart

### 1. Konfiguration

Stellen Sie sicher, dass `.env` konfiguriert ist:

```bash
# BBB Configuration
BBB_DEFAULT_ROOM_URL=https://bbb.example.eu/b/raum-name
BBB_DEFAULT_USERNAME=RaspberryMeet

# Web Interface
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_USERNAME=admin
WEB_PASSWORD=change-this-password
```

### 2. Server starten

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Web-Server starten
python run_web.py
```

### 3. Browser öffnen

Öffnen Sie in Ihrem Browser:

```
http://raspberrypi.local:8080
```

Oder mit IP-Adresse:

```
http://192.168.1.XXX:8080
```

**Login:**
- Benutzername: `admin` (oder konfiguriert in .env)
- Passwort: Ihr Passwort aus .env

---

## API-Endpunkte

### Status abrufen
```bash
GET /api/status
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Response:**
```json
{
  "state": "idle",
  "current_room": null,
  "meeting_duration": null,
  "uptime": 0,
  "timestamp": "2025-11-15T10:30:00"
}
```

### Meeting beitreten (Standard-Raum)
```bash
POST /api/meeting/join-default
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully joined meeting",
  "state": "active"
}
```

### Meeting beitreten (benutzerdefiniert)
```bash
POST /api/meeting/join
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

{
  "room_url": "https://bbb.example.eu/b/custom-room",
  "username": "Custom User",
  "password": "room-password"
}
```

### Meeting verlassen
```bash
POST /api/meeting/leave
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

### WebSocket-Status
```bash
WS /ws/status
```

Empfängt Echtzeit-Updates:
```json
{
  "state": "active",
  "current_room": "https://bbb.example.eu/b/room",
  "duration": 120,
  "timestamp": "2025-11-15T10:32:00"
}
```

---

## Entwicklung

### Server mit Auto-Reload starten

Für Entwicklung mit automatischem Reload:

```python
# In src/web/api.py am Ende ändern:
uvicorn.run(
    "src.web.api:app",
    host=config.web.host,
    port=config.web.port,
    reload=True,  # <- Auto-reload aktivieren
    log_level="debug",
)
```

Oder direkt:

```bash
uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8080
```

### Frontend-Struktur

```
src/web/
├── api.py                      # FastAPI App
├── auth.py                     # Authentifizierung
├── static/
│   └── style.css              # CSS-Styles
└── templates/
    ├── dashboard.html         # Haupt-Dashboard
    └── partials/
        ├── status_badge.html  # Status-Badge-Partial
        ├── status_info.html   # Status-Info-Partial
        └── quick_actions.html # Quick-Actions-Partial
```

### Technologie-Stack

- **Backend:** FastAPI 0.109.0
- **Frontend:** HTML + htmx 1.9.10
- **WebSocket:** FastAPI WebSockets
- **Auth:** HTTP Basic Authentication
- **Templates:** Jinja2
- **Styling:** Vanilla CSS (keine Frameworks)

---

## Zugriff von anderen Geräten

### Raspberry Pi IP-Adresse finden

```bash
hostname -I
```

Ausgabe: `192.168.1.XXX`

### Von anderen Geräten im Netzwerk

**Desktop/Laptop:**
```
http://192.168.1.XXX:8080
```

**Smartphone:**
- Mit demselben WiFi verbinden
- Browser öffnen: `http://192.168.1.XXX:8080`

**Hostname verwenden (wenn mDNS aktiv):**
```
http://raspberrypi.local:8080
```

---

## Sicherheit

### Passwort ändern

**Wichtig:** Ändern Sie das Standard-Passwort!

```bash
nano .env
```

Ändern Sie:
```bash
WEB_PASSWORD=ihr-sicheres-passwort-hier
```

### HTTPS aktivieren (optional)

Für Produktionsumgebungen sollten Sie einen Reverse-Proxy verwenden:

**Mit nginx:**
```nginx
server {
    listen 443 ssl;
    server_name raspberrypi.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Firewall-Regel

Zugriff nur vom lokalen Netzwerk:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 8080
```

---

## Fehlerbehebung

### "Connection refused"

**Problem:** Server läuft nicht oder falsche Adresse

**Lösung:**
```bash
# Server-Status prüfen
ps aux | grep run_web

# Logs prüfen
python run_web.py
```

### "401 Unauthorized"

**Problem:** Falsche Login-Daten

**Lösung:**
```bash
# .env-Datei prüfen
cat .env | grep WEB_

# Passwort zurücksetzen
nano .env
```

### WebSocket verbindet nicht

**Problem:** Proxy blockiert WebSocket-Verbindung

**Lösung:**
- Direkten Zugriff ohne Proxy testen
- nginx/Apache mit WebSocket-Support konfigurieren

### Browser zeigt nichts an

**Problem:** Chromium-Browser läuft headless

**Lösung:**
```bash
# In .env setzen:
WEB_HEADLESS_BROWSER=false
```

### "Template not found"

**Problem:** Templates-Verzeichnis fehlt

**Lösung:**
```bash
# Verzeichnisse erstellen
mkdir -p src/web/templates/partials
mkdir -p src/web/static
```

---

## Systemd-Service (Autostart)

Service-Datei: `/etc/systemd/system/raspberrymeet-web.service`

```ini
[Unit]
Description=RaspberryMeet Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RaspberryMeet
Environment="PATH=/home/pi/RaspberryMeet/venv/bin"
ExecStart=/home/pi/RaspberryMeet/venv/bin/python run_web.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Aktivieren:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable raspberrymeet-web
sudo systemctl start raspberrymeet-web
sudo systemctl status raspberrymeet-web
```

---

## Screenshots

### Dashboard
- Status-Übersicht mit Echtzeit-Updates
- Schnellzugriff-Buttons (Join/Leave)
- Benutzerdefinierte Raum-URL-Eingabe

### Status-Badges
- 🟢 **Bereit** (idle) - System bereit für Meeting-Beitritt
- 🔵 **Trete bei** (joining) - Browser startet und tritt bei
- 🟢 **Im Meeting** (active) - Erfolgreich im Meeting
- 🟠 **Verlasse** (leaving) - Meeting wird verlassen
- 🔴 **Fehler** (error) - Fehler beim Beitritt/Verlassen

---

## Performance

**Empfohlene Hardware:**
- Raspberry Pi 4 (2GB+ RAM)
- Für gleichzeitiges BBB-Meeting + Web-Interface: 4GB RAM empfohlen

**Ressourcenverbrauch:**
- FastAPI-Server: ~30-50 MB RAM
- Chromium (headless): ~200-300 MB RAM
- Chromium (GUI): ~500-800 MB RAM

**Tipps:**
- Headless-Modus nutzen wenn möglich
- Alte WebSocket-Verbindungen werden automatisch bereinigt
- Browser-Controller läuft im selben Prozess (kein Extra-Service)

---

## Roadmap

- [ ] JWT-Token-Authentifizierung
- [ ] Multi-Raum-Verwaltung
- [ ] Meeting-Historie
- [ ] Konfigurationseditor im Web-Interface
- [ ] GPIO-Status-Anzeige
- [ ] Kalender-Integration-Status
- [ ] System-Logs-Viewer
- [ ] Dark Mode
- [ ] Mehrsprachigkeit (EN/DE)

---

**Version:** 0.1.0
**Status:** ✅ Funktionsfähig (MVP)
