# Audio/Video Setup - RaspberryMeet

**Konfiguration von Konferenz-Freisprecheinrichtungen und Webcams**

Dieses Dokument erklärt die Einrichtung und Konfiguration von Audio- und Video-Hardware für optimale BigBlueButton-Meetings.

---

## 📋 Übersicht

RaspberryMeet bietet automatische Erkennung und Konfiguration von:
- **Konferenz-Freisprecheinrichtungen** (USB oder Bluetooth)
- **USB-Webcams**
- **HDMI-Audio** (Fallback)

### Unterstützte Geräte

**Empfohlene Konferenz-Speakerphones:**
- Jabra Speak 510 (USB/Bluetooth)
- Anker PowerConf (USB/Bluetooth)
- eMeet M2 (USB/Bluetooth)
- Logitech (verschiedene Modelle)

**Webcams:**
- Alle V4L2-kompatiblen USB-Webcams
- Logitech C920, C922, C930e
- Raspberry Pi Camera Module (mit Adapter)

---

## 🚀 Schnellstart

### Option 1: Automatische Konfiguration (Empfohlen)

Der Audio-Manager konfiguriert Geräte automatisch beim Start:

```bash
# Meeting-Manager startet automatisch Audio-Konfiguration
python -m src.orchestrator.main
```

**Was passiert:**
1. PulseAudio-Verbindung wird hergestellt
2. Verfügbare Audio-Geräte werden erkannt
3. Beste verfügbare Konferenz-Speakerphone wird ausgewählt
4. Als Default-Device gesetzt
5. Browser nutzt automatisch diese Geräte

### Option 2: Manuelle Konfiguration

Verwenden Sie die Setup-Scripts:

```bash
# Audio-Geräte konfigurieren
./scripts/setup_audio.sh

# Bluetooth-Speakerphone pairen
./scripts/pair_bluetooth.sh

# Hardware testen
python scripts/test_audio_video.py
```

---

## 🔧 USB-Speakerphone einrichten

### Schritt 1: Anschließen

1. USB-Kabel einstecken
2. Gerät einschalten (falls mit Akku)
3. Warten bis LED leuchtet/blinkt

### Schritt 2: Erkennung prüfen

```bash
# Audio-Geräte auflisten
pactl list sources short  # Mikrofone
pactl list sinks short    # Lautsprecher

# Sollte zeigen: "Jabra Speak 510" oder ähnlich
```

### Schritt 3: Als Default setzen

**Automatisch:**
```bash
# Meeting-Manager konfiguriert automatisch
python demo_gpio_meeting.py
```

**Manuell:**
```bash
# Setup-Script ausführen
./scripts/setup_audio.sh

# Oder direkt mit pactl:
pactl set-default-source <device-name>
pactl set-default-sink <device-name>
```

### Schritt 4: Testen

```bash
# Hardware-Test
python scripts/test_audio_video.py

# Oder manuell:
speaker-test -t wav -c 2  # Lautsprecher testen
arecord -d 3 test.wav && aplay test.wav  # Mikrofon testen
```

---

## 📡 Bluetooth-Speakerphone einrichten

### Voraussetzungen

```bash
# Bluetooth-Pakete installieren
sudo apt update
sudo apt install -y bluez bluez-tools pulseaudio-module-bluetooth

# Bluetooth-Service starten
sudo systemctl start bluetooth
sudo systemctl enable bluetooth
```

### Pairing-Prozess

**Mit Script (Empfohlen):**

```bash
./scripts/pair_bluetooth.sh
```

**Schritt-für-Schritt:**

1. **Bluetooth-Modus aktivieren:**
   - Schalten Sie Ihr Speakerphone ein
   - Drücken Sie die Bluetooth-Taste (meist ~3 Sekunden)
   - LED sollte blinken (Pairing-Modus)

2. **Pairing-Wizard starten:**
   ```
   Select: 1) Auto-pair wizard (recommended)
   ```

3. **Gerät auswählen:**
   - Script scannt 15 Sekunden
   - Zeigt gefundene Geräte mit MAC-Adresse
   - Geben Sie MAC-Adresse ein

4. **Verbindung testen:**
   ```bash
   # Verbundene Geräte prüfen
   bluetoothctl paired-devices
   bluetoothctl info <MAC>
   ```

### Bluetooth-Probleme beheben

**Gerät wird nicht gefunden:**
```bash
# Bluetooth neu starten
sudo systemctl restart bluetooth

# Erneut scannen
bluetoothctl scan on
# 15 Sekunden warten
bluetoothctl scan off
bluetoothctl devices
```

**Verbindung bricht ab:**
```bash
# Gerät neu verbinden
bluetoothctl connect <MAC>

# PulseAudio neu laden
pulseaudio -k
pulseaudio --start
```

**Kein Audio über Bluetooth:**
```bash
# Bluetooth-Audio-Module laden
pactl load-module module-bluetooth-discover

# Default setzen
pactl set-default-source bluez_source.<MAC>
pactl set-default-sink bluez_sink.<MAC>
```

---

## 📹 Webcam einrichten

### Erkennung prüfen

```bash
# Video-Geräte auflisten
ls -l /dev/video*

# Gerät-Info anzeigen (benötigt v4l2-utils)
sudo apt install v4l2-utils
v4l2-ctl --device=/dev/video0 --info
v4l2-ctl --device=/dev/video0 --list-formats-ext
```

### Webcam testen

```bash
# Mit Hardware-Test-Script
python scripts/test_audio_video.py

# Manuell mit VLC (falls installiert)
vlc v4l2:///dev/video0

# Oder mit ffplay
ffplay /dev/video0
```

### Mehrere Webcams

Wenn Sie mehrere Kameras haben:

```bash
# Alle Kameras auflisten
for dev in /dev/video*; do
  echo "$dev:"
  v4l2-ctl --device=$dev --info | grep "Card type"
done

# Beste Kamera wird automatisch gewählt (/dev/video0)
```

---

## ⚙️ Automatische Device-Auswahl

### Wie es funktioniert

Der `AudioVideoManager` wählt Geräte automatisch basierend auf Priorität:

**Priorität (höchste zuerst):**
1. Jabra Speak 510
2. Anker PowerConf
3. eMeet M2
4. Logitech (verschiedene)
5. HDMI Audio (Fallback)
6. Erstes verfügbares Gerät

**Code-Beispiel:**
```python
from src.orchestrator.audio_manager import AudioVideoManager

# Audio-Manager erstellen
audio = AudioVideoManager()

# Auto-Konfiguration
audio.configure_audio()

# Verfügbare Geräte anzeigen
sources = audio.get_audio_sources()
for source in sources:
    print(f"Mikrofon: {source.description}")

sinks = audio.get_audio_sinks()
for sink in sinks:
    print(f"Lautsprecher: {sink.description}")
```

### Eigene Präferenzen

In `config/audio_devices.yaml`:

```yaml
preferred_devices:
  - Jabra Speak 510
  - Anker PowerConf
  - Your Custom Device Name
  - HDMI Audio
```

Oder in Code:

```python
audio = AudioVideoManager(preferred_devices=[
    "My Speakerphone",
    "HDMI Audio",
])
```

---

## 🔍 Hardware-Test

### Vollständiger Test

```bash
python scripts/test_audio_video.py
```

**Was wird getestet:**
- ✅ PulseAudio-Verfügbarkeit
- ✅ Audio-Eingabegeräte (Mikrofone)
- ✅ Audio-Ausgabegeräte (Lautsprecher)
- ✅ Video-Geräte (Webcams)
- ✅ Bevorzugte Konferenz-Geräte
- ✅ Default-Device-Konfiguration

**Beispiel-Ausgabe:**
```
🎤 Audio Device Test
════════════════════════════════════════════════════════════
✅ PulseAudio is available

Audio Input Devices (Microphones):
────────────────────────────────────────────────────────────
  ✓ Jabra Speak 510 [DEFAULT]
    Built-in Audio Analog Stereo

Audio Output Devices (Speakers):
────────────────────────────────────────────────────────────
  ✓ Jabra Speak 510 [DEFAULT]
    HDMI Audio

📹 Video Device Test
════════════════════════════════════════════════════════════
Found 1 webcam(s):

  1. Logitech HD Pro Webcam C920
     Device: /dev/video0

✅ Video devices detected successfully
```

### Einzelne Komponenten testen

**Nur Audio:**
```bash
# Mikrofon testen
arecord -d 3 -f cd test.wav
aplay test.wav

# Lautsprecher testen
speaker-test -t wav -c 2
```

**Nur Video:**
```bash
# Bild aufnehmen
v4l2-ctl --device=/dev/video0 --set-fmt-video=width=1920,height=1080
fswebcam -r 1920x1080 test.jpg

# Video ansehen
vlc v4l2:///dev/video0
```

---

## 🛠️ Troubleshooting

### Problem: Kein Audio-Gerät erkannt

**Symptom:** `pactl list sources` zeigt nur "monitor"

**Lösung:**
```bash
# PulseAudio neu starten
pulseaudio -k
pulseaudio --start

# USB neu einstecken
# Oder für Bluetooth: bluetoothctl connect <MAC>

# Logs prüfen
journalctl -u pulseaudio -f
```

### Problem: Audio-Qualität schlecht

**Symptom:** Echo, Rauschen, leise

**Lösung:**
```bash
# Sample-Rate erhöhen
sudo nano /etc/pulse/daemon.conf
# Ändern:
# default-sample-rate = 48000
# alternate-sample-rate = 44100

# PulseAudio neu starten
pulseaudio -k
```

### Problem: Webcam zeigt schwarz

**Symptom:** `/dev/video0` existiert, aber kein Bild

**Lösung:**
```bash
# Berechtigungen prüfen
ls -l /dev/video*
# Sollte zeigen: crw-rw---- 1 root video

# User zur video-Gruppe hinzufügen
sudo usermod -a -G video pi
# Neu anmelden!

# Gerät zurücksetzen
sudo rmmod uvcvideo
sudo modprobe uvcvideo
```

### Problem: Bluetooth verbindet nicht

**Symptom:** Pairing erfolgreich, aber keine Verbindung

**Lösung:**
```bash
# Bluetooth-Profile prüfen
pactl list cards

# Profil auf "a2dp_sink" setzen
pactl set-card-profile <card-id> a2dp_sink

# Bluetooth-Audio-Modul neu laden
pactl unload-module module-bluetooth-discover
pactl load-module module-bluetooth-discover
```

### Problem: Falsche Audio-Defaults

**Symptom:** Browser nutzt falsches Mikrofon

**Lösung:**
```bash
# Default manuell setzen
pactl set-default-source <device-name>
pactl set-default-sink <device-name>

# In ~/.config/pulse/default.pa festlegen:
set-default-source alsa_input.usb-xxx
set-default-sink alsa_output.usb-xxx

# Oder Setup-Script verwenden:
./scripts/setup_audio.sh
```

---

## 📊 System-Informationen

### Audio-System prüfen

```bash
# PulseAudio-Status
pactl info

# Alle Geräte
pactl list

# Default-Geräte
pactl get-default-source  # Mikrofon
pactl get-default-sink    # Lautsprecher

# Lautstärke
pactl get-source-volume @DEFAULT_SOURCE@
pactl get-sink-volume @DEFAULT_SINK@
```

### Video-System prüfen

```bash
# Alle Video-Geräte
v4l2-ctl --list-devices

# Unterstützte Formate
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Aktuelle Einstellungen
v4l2-ctl --device=/dev/video0 --all
```

### Mit Python-Script

```python
from src.orchestrator.audio_manager import AudioVideoManager

audio = AudioVideoManager()
info = audio.get_system_info()

print(f"PulseAudio: {info['pulseaudio_available']}")
print(f"Default Input: {info['default_source']}")
print(f"Default Output: {info['default_sink']}")
print(f"Audio Inputs: {len(info['audio_sources'])}")
print(f"Audio Outputs: {len(info['audio_sinks'])}")
print(f"Webcams: {len(info['video_devices'])}")
```

---

## 🔒 Berechtigungen

### Audio-Zugriff

```bash
# User zur audio-Gruppe hinzufügen
sudo usermod -a -G audio pi

# Für PulseAudio
sudo usermod -a -G pulse-access pi
```

### Video-Zugriff

```bash
# User zur video-Gruppe hinzufügen
sudo usermod -a -G video pi

# Neu anmelden:
newgrp video
# Oder komplett ausloggen/einloggen
```

### Bluetooth-Zugriff

```bash
# User zur bluetooth-Gruppe hinzufügen
sudo usermod -a -G bluetooth pi
```

---

## 📝 Best Practices

### Für optimale Audio-Qualität

1. **USB-Verbindung bevorzugen**
   - Stabiler als Bluetooth
   - Bessere Audio-Qualität
   - Keine Pairing-Probleme

2. **Konferenz-Speakerphone verwenden**
   - Eingebautes Echo-Cancelling
   - 360°-Mikrofone
   - USB-Hub wenn mehrere USB-Geräte

3. **Sample-Rate konfigurieren**
   ```bash
   # /etc/pulse/daemon.conf
   default-sample-rate = 48000
   ```

4. **Automatische Lautstärke deaktivieren**
   - Manche Geräte haben Auto-Gain
   - Kann zu Problemen führen

### Für Bluetooth

1. **Gerät nah am Pi halten** (< 5 Meter)
2. **Interferenzen vermeiden** (WLAN auf 5GHz)
3. **Akku voll laden** (schwacher Akku = schlechte Verbindung)
4. **A2DP-Profil nutzen** (beste Qualität)

### Für Webcams

1. **Gute Beleuchtung** (kein Gegenlicht)
2. **USB 3.0 Port** (bessere Bandbreite)
3. **1080p bevorzugen** (4K kann zu viel sein für Pi)

---

## 🚀 Integration in BBB-Meetings

### Automatischer Ablauf

1. **System startet:**
   ```
   Audio-Manager konfiguriert Geräte
   Browser startet mit korrekten Defaults
   ```

2. **Meeting beitreten:**
   ```
   Browser fragt nach Mikrofon/Kamera-Berechtigung
   Playwright klickt "Erlauben"
   BBB nutzt konfigurierte Default-Devices
   ```

3. **Im Meeting:**
   ```
   Audio/Video läuft über Konferenz-Speakerphone
   Automatisches Echo-Cancelling
   Optimale Qualität
   ```

### Manuelle Kontrolle

Im Browser (während des Meetings):
- Mikrofon stumm/laut: BBB-Interface
- Kamera an/aus: BBB-Interface
- Device wechseln: BBB Einstellungen

---

## 📖 Weitere Ressourcen

### Dokumentation

- **PulseAudio:** https://www.freedesktop.org/wiki/Software/PulseAudio/
- **Bluetooth:** https://www.bluetooth.com/
- **V4L2:** https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html

### Tools

- **pavucontrol:** GUI für PulseAudio
  ```bash
  sudo apt install pavucontrol
  pavucontrol
  ```

- **blueman:** GUI für Bluetooth
  ```bash
  sudo apt install blueman
  blueman-manager
  ```

- **guvcview:** Webcam-Viewer
  ```bash
  sudo apt install guvcview
  guvcview
  ```

---

**Version:** 1.0
**Letzte Aktualisierung:** 2025-11-15
