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

## Weitere Scripts (geplant)

- `install.sh` - Automatische Installation und Setup
- `setup_audio.sh` - PulseAudio-Konfiguration
- `setup_display.sh` - X11/Kiosk-Modus-Setup
- `pair_bluetooth.sh` - Bluetooth-Freisprecheinrichtung-Pairing
- `test_hardware.sh` - Hardware-Test-Utility
- `update.sh` - Update-Deployment

---

**Hinweis:** Alle Scripts sind im Repository dokumentiert und sicher zu verwenden.
