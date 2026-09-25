# Philips-AEA3000-00-Noise-Guard

Das Skript ist als reines **Terminal-Tool** aufgebaut. Es zeigt dir in Echtzeit:

1. Eine **visuelle Lautstärke-Anzeige (ASCII-Balken)**.
2. Den aktuellen Status (OBEN / OK vs. **ALARM**).
3. Eine Statistik über Spitzenwerte (Peak) und wie oft das Limit im aktuellen Durchlauf überschritten wurde.

## Installationsanweisungen

Egal ob auf deinem **Laptop** (Linux/Mac/WSL) oder später auf dem **Raspberry Pi**, benötigst du Python 3 und die Bibliothek `PyAudio` zur Audioverarbeitung sowie `requests` für openHAB.

### Auf dem Raspberry Pi / Linux-Laptop:

Öffne das Terminal und führe folgende Befehle aus:

```bash
# 1. Systempakete für Audio-Unterstützung installieren
sudo apt-get update
sudo apt-get install -y python3-pyaudio portaudio19-dev python3-pip

# 2. Benötigte Python-Bibliotheken installieren
pip3 install pyaudio numpy requests

```

### Auf einem Windows-Laptop (PowerShell / CMD):

```cmd
pip install pyaudio numpy requests
```

---

## Befehle zum Ausführen

### Mikrofon-Index suchen

```bash
python3 decibel_guard_terminal.py --list-devices
```

### Monitor im Terminal starten

Gib den Index deiner Sabrent-Soundkarte (z. B. `1`) an:

```bash
python3 decibel_guard_terminal.py --device 1 --zone Partyraum
```

### Individuelle Parameter setzen (Optional)

Du kannst Tag-/Nacht-Limits und die Uhrzeit direkt als Befehl übergeben:

```bash
python3 decibel_guard_terminal.py --device 1 --zone Wohnzimmer --limit-day 80.0 --limit-night 50.0 --quiet-hour 21

```

---

## Was du im Terminal siehst:

Sobald das Skript läuft, baut es sich im Terminal als übersichtliches **Live-Dashboard** auf und aktualisiert sich 10-mal pro Sekunde:

```text
============================================================
  STANDALONE LÄRMSCHUTZ | Zone: 'Partyraum'
============================================================
 Status:          🚨 ALARM (Zulaut!) 🚨
 Modus:           NACHTMODUS 🌙 (Nachtruhe ab 22:00 Uhr)
 Aktueller Pegel:  62.4 dB  [▒▒▒▒▒▒▒▒▒▒▒▒▒▒█████|░░░░░░░░░░]
 Grenzwert:        55.0 dB
------------------------------------------------------------
 Höchster Peak:    78.1 dB
 Anz. Alarme:     14
 Laufzeit:        00:04:12
============================================================
 [Strg+C zum Beenden]

```
