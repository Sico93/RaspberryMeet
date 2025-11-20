# GPIO Setup - RaspberryMeet

**Hardware-Button-Steuerung für BigBlueButton-Meetings**

Dieses Dokument beschreibt die GPIO-Verkabelung und -Konfiguration für die Hardware-Button-Steuerung.

---

## 📋 Übersicht

Mit der GPIO-Integration können Sie:
- **Ein-Button-Bedienung:** Drücken Sie einen Taster, um dem Standard-Meeting beizutreten oder es zu verlassen
- **LED-Status-Anzeige:** Sehen Sie den aktuellen System-Status auf einen Blick
- **Tastatur-freie Bedienung:** Keine Maus oder Tastatur erforderlich

---

## 🔌 Hardware-Anforderungen

### Komponenten

| Komponente | Anzahl | Beschreibung |
|------------|--------|--------------|
| Taster (Pushbutton) | 1 | Momentary pushbutton (NO - Normally Open) |
| LED Grün | 1 | 3mm oder 5mm LED, grün |
| LED Rot | 1 | 3mm oder 5mm LED, rot |
| Widerstand 220Ω | 2 | Für LEDs |
| Jumper-Kabel | mehrere | Für Verbindungen |
| Breadboard | 1 | Optional, zum Testen |

### Raspberry Pi GPIO-Pins

**Standard-Pin-Belegung (BCM-Nummerierung):**

| Funktion | GPIO (BCM) | Physischer Pin | Beschreibung |
|----------|------------|----------------|--------------|
| Join/Leave Button | GPIO 17 | Pin 11 | Taster für Meeting-Join/Leave |
| Status LED (Grün) | GPIO 23 | Pin 16 | Grün = Bereit |
| Status LED (Rot) | GPIO 24 | Pin 18 | Rot = Im Meeting |
| Ground (GND) | - | Pin 6, 9, 14, 20, 25, 30, 34, 39 | Masse |

**📌 Wichtig:** Verwenden Sie BCM-Nummerierung (nicht physische Pin-Nummern)!

---

## 🔧 Verkabelung

### Schaltplan

```
Raspberry Pi GPIO
┌─────────────────────────────────┐
│                                 │
│  GPIO 17 (Pin 11) ───┐          │
│                      │          │
│  GPIO 23 (Pin 16) ───┼─→ LEDs   │
│                      │          │
│  GPIO 24 (Pin 18) ───┘          │
│                                 │
│  GND (Pin 6) ──────────────→ GND│
│                                 │
└─────────────────────────────────┘
```

### Taster-Verkabelung

```
       Raspberry Pi
      ┌──────────┐
      │          │
GPIO17│  11      │
──────┤          │
      │          │
  GND │  6       │
──────┤          │
      │          │
      └──────────┘
         │    │
         │    │
         │    └────┐
         │         │
      ┌──▼──┐      │
      │     │      │
      │  S  │      │  S = Taster (Pushbutton)
      │     │      │
      └──┬──┘      │
         │         │
         └─────────┘
```

**Verbindungen:**
1. GPIO 17 (Pin 11) → Eine Seite des Tasters
2. GND (Pin 6) → Andere Seite des Tasters

**Hinweis:** Der interne Pull-Up-Widerstand wird per Software aktiviert (gpiozero macht das automatisch).

### LED-Verkabelung

**Grüne LED:**
```
GPIO 23 ──→ 220Ω ──→ LED+ (long leg) ──→ LED- (short leg) ──→ GND
```

**Rote LED:**
```
GPIO 24 ──→ 220Ω ──→ LED+ (long leg) ──→ LED- (short leg) ──→ GND
```

**LED-Polarität beachten:**
- **Langes Bein (+):** Anode - verbinden mit Widerstand (von GPIO)
- **Kurzes Bein (-):** Kathode - verbinden mit GND

### Breadboard-Aufbau

```
     Raspberry Pi
    ┌────────────┐
    │ GPIO 17    ├───┐
    │ GPIO 23    ├───┼───┐
    │ GPIO 24    ├───┼───┼───┐
    │ GND        ├───┼───┼───┼────┐
    └────────────┘   │   │   │    │
                     │   │   │    │
        ┌────────────▼───▼───▼────▼─────┐
        │  Breadboard                   │
        │                                │
        │  [Taster]    [LED🟢]  [LED🔴] │
        │     │         │   │    │   │  │
        │     └─────────┴───┴────┴───┴──┤ GND Rail
        │                                │
        └────────────────────────────────┘
```

---

## ⚙️ Software-Konfiguration

### .env-Datei

Bearbeiten Sie `.env` und setzen Sie:

```bash
# GPIO Configuration
GPIO_ENABLED=true
GPIO_JOIN_BUTTON_PIN=17
GPIO_LEAVE_BUTTON_PIN=27   # Derzeit nicht verwendet
GPIO_MUTE_BUTTON_PIN=22    # Derzeit nicht verwendet
GPIO_STATUS_LED_GREEN_PIN=23
GPIO_STATUS_LED_RED_PIN=24
```

### Pin-Nummern ändern

Falls Sie andere Pins verwenden möchten:

1. Bearbeiten Sie `.env`
2. Ändern Sie die entsprechenden `GPIO_*_PIN` Werte
3. Passen Sie die Verkabelung entsprechend an

**Empfohlene GPIO-Pins:**
- Verwenden Sie GPIO 2-27 (vermeiden Sie GPIO 0, 1 für I2C)
- Vermeiden Sie Pin 8 (GPIO 14) und Pin 10 (GPIO 15) - UART
- Vermeiden Sie Pins mit speziellen Funktionen (SPI, I2C) wenn möglich

---

## 🧪 Hardware testen

### Test 1: GPIO-Basis-Test

```bash
# GPIO-Test ohne Browser
python scripts/test_gpio.py
```

**Was wird getestet:**
1. LED-Zustände (alle Farben durchlaufen)
2. Button-Erkennung (drücken und LED-Wechsel beobachten)

**Erwartetes Verhalten:**
- LEDs schalten durch verschiedene Zustände
- Bei Button-Druck wechselt LED-Farbe
- Logs zeigen Button-Drücke an

### Test 2: Kompletter Meeting-Test

```bash
# Vollständiger Test mit Browser-Integration
python demo_gpio_meeting.py
```

**Was wird getestet:**
1. Button-Druck → Meeting beitreten
2. LED wechselt zu ROT (im Meeting)
3. Erneuter Button-Druck → Meeting verlassen
4. LED wechselt zu GRÜN (bereit)

---

## 💡 LED-Status-Bedeutung

| LED-Status | Farbe | Bedeutung |
|------------|-------|-----------|
| 🟢 Grün (konstant) | Grün | System bereit, kein Meeting aktiv |
| 🟡 Gelb (beide an) | Grün + Rot | System tritt Meeting bei oder verlässt es |
| 🔴 Rot (konstant) | Rot | Im Meeting aktiv |
| 🔴 Rot (blinkend) | Rot blinkt | Fehler aufgetreten |
| ⚫ Aus | Keine | System aus oder nicht initialisiert |

---

## 🎮 Bedienung

### Ein-Button-Steuerung (Toggle)

**Workflow:**

1. **System startet** → LED 🟢 (Grün = Bereit)

2. **Button drücken** → LED 🟡 (Gelb = Trete bei...)
   - System öffnet Browser
   - Tritt BBB-Raum bei
   - Aktiviert Mikrofon

3. **Meeting aktiv** → LED 🔴 (Rot = Im Meeting)
   - Bleiben Sie im Meeting so lange Sie wollen
   - LED bleibt ROT

4. **Button erneut drücken** → LED 🟡 (Gelb = Verlasse...)
   - System verlässt Meeting
   - Schließt Browser-Tabs

5. **Zurück zu Bereit** → LED 🟢 (Grün = Bereit)
   - System bereit für nächstes Meeting

### Fehlerfall

Wenn LED 🔴 **blinkt**:
- Ein Fehler ist aufgetreten (z.B. BBB-Server nicht erreichbar)
- System setzt sich nach 5 Sekunden automatisch auf BEREIT zurück
- LED wechselt zurück zu 🟢 (Grün)
- Sie können es erneut versuchen

---

## 🔍 Troubleshooting

### Problem: LEDs leuchten nicht

**Mögliche Ursachen:**
1. **Falsche Verkabelung**
   - Prüfen Sie Polarität (langes Bein = +, kurzes Bein = -)
   - Prüfen Sie Widerstände (220Ω)
   - Prüfen Sie GND-Verbindung

2. **GPIO nicht aktiviert**
   - Prüfen Sie `.env`: `GPIO_ENABLED=true`
   - Prüfen Sie Logs: `GPIO hardware not available`

3. **Falsche Pin-Nummern**
   - `.env` verwendet BCM-Nummerierung (nicht physisch!)
   - GPIO 23 = Pin 16 (physisch)
   - GPIO 24 = Pin 18 (physisch)

**Lösung:**
```bash
# Test-Script ausführen
python scripts/test_gpio.py

# Logs prüfen
# Bei "Mock LED" → GPIO nicht verfügbar
# Bei "LED X: ON" → Software funktioniert, Hardware prüfen
```

### Problem: Button-Drücke werden nicht erkannt

**Mögliche Ursachen:**
1. **Taster nicht verbunden**
   - GPIO 17 → eine Seite des Tasters
   - GND → andere Seite des Tasters

2. **Falscher Taster-Typ**
   - Verwenden Sie Momentary (NO = Normally Open)
   - NICHT Latching/Toggle

3. **Software nicht gestartet**
   - Orchestrator muss laufen

**Lösung:**
```bash
# GPIO-Test ausführen und Button drücken
python scripts/test_gpio.py

# Logs prüfen:
# "Button pressed!" sollte erscheinen
```

### Problem: "GPIO not available"

**Ursache:** Nicht auf Raspberry Pi oder gpiozero nicht installiert

**Lösung:**
```bash
# gpiozero installieren
pip install gpiozero RPi.GPIO

# Auf Raspberry Pi ausführen (nicht auf Desktop-PC)
```

### Problem: "Permission denied" bei GPIO-Zugriff

**Ursache:** User hat keine GPIO-Berechtigung

**Lösung:**
```bash
# User zur gpio-Gruppe hinzufügen
sudo usermod -a -G gpio $USER

# ODER als Alternative: dialout-Gruppe
sudo usermod -a -G dialout $USER

# Neu anmelden oder:
newgrp gpio

# Script erneut ausführen
```

### Problem: LED zu hell/zu dunkel

**Lösung:**
- **Zu hell:** Größeren Widerstand verwenden (z.B. 330Ω statt 220Ω)
- **Zu dunkel:** Kleineren Widerstand verwenden (z.B. 150Ω, NICHT unter 100Ω!)
- **Standard:** 220Ω ist für die meisten LEDs ideal

---

## 🚀 Produktiv-Betrieb

### Autostart mit systemd

Systemd-Service erstellen (`/etc/systemd/system/raspberrymeet.service`):

```ini
[Unit]
Description=RaspberryMeet Orchestrator
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RaspberryMeet
Environment="PATH=/home/pi/RaspberryMeet/venv/bin"
ExecStart=/home/pi/RaspberryMeet/venv/bin/python -m src.orchestrator.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Aktivieren:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable raspberrymeet
sudo systemctl start raspberrymeet
sudo systemctl status raspberrymeet
```

**Logs anzeigen:**
```bash
sudo journalctl -u raspberrymeet -f
```

---

## 🛡️ Sicherheitshinweise

### Elektrische Sicherheit

1. **Niemals GPIO-Pins mit mehr als 3.3V verbinden!**
   - GPIO-Pins sind 3.3V-Pins
   - 5V (vom Raspberry Pi 5V-Pin) kann GPIO zerstören!

2. **Immer Widerstände für LEDs verwenden**
   - Mindestens 100Ω (empfohlen: 220Ω)
   - Ohne Widerstand kann LED oder GPIO beschädigt werden

3. **Polarität beachten**
   - LEDs haben Polung (+ und -)
   - Falsches Anschließen beschädigt LED

4. **Stromstärke begrenzen**
   - Maximaler Strom pro GPIO: 16 mA
   - Alle GPIOs zusammen: max. 50 mA
   - Nicht mehrere LEDs parallel ohne Widerstände!

### Hardware-Schutz

**Empfohlen:**
- Verwenden Sie ein Gehäuse für Raspberry Pi
- Befestigen Sie Verkabelung (nicht lose hängen lassen)
- Verwenden Sie farbcodierte Jumper-Kabel
- Beschriften Sie Komponenten
- Dokumentieren Sie Änderungen

---

## 📸 Beispiel-Aufbau

### Minimalaufbau (Breadboard)

```
Komponenten:
- 1× Raspberry Pi 4
- 1× Breadboard
- 1× Taster
- 1× LED grün (mit 220Ω)
- 1× LED rot (mit 220Ω)
- Jumper-Kabel

Verbindungen:
1. Pi GPIO 17 → Breadboard → Taster → GND
2. Pi GPIO 23 → 220Ω → LED grün → GND
3. Pi GPIO 24 → 220Ω → LED rot → GND
```

### Permanenter Aufbau (Gehäuse)

**Empfehlungen:**
- Externes Gehäuse für Button und LEDs
- Längere Kabel (20-30cm) für flexibles Aufstellen
- Beschriftung: "Meeting starten/beenden"
- Grünes Gehäuse für LED, Roter Rahmen um Button

---

## 🔗 Weiterführende Links

- **gpiozero Dokumentation:** https://gpiozero.readthedocs.io/
- **Raspberry Pi GPIO Pinout:** https://pinout.xyz/
- **LED-Widerstand-Rechner:** https://www.digikey.de/de/resources/conversion-calculators/conversion-calculator-led-series-resistor

---

## 📝 Changelog

- **2025-11-15:** GPIO-Implementation mit Toggle-Button und LED-Status
- **2025-11-15:** Test-Scripts und Dokumentation erstellt

---

**Viel Erfolg beim Aufbau! 🚀**
