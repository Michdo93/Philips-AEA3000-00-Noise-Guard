import argparse
import datetime
import math
import os
import sys
import time
import numpy as np
import pyaudio

# ==================== STANDARDS ====================
DEFAULT_QUIET_HOUR_START = 22  # Ab 22:00 Uhr Nachtmodus
DEFAULT_MAX_DB_DAY = 75.0      # Tag-Limit in dB
DEFAULT_MAX_DB_NIGHT = 55.0    # Nacht-Limit in dB
# ===================================================

def calculate_db(audio_data):
    """Berechnet die relative Lautstärke (RMS) in dB aus den Mikrofon-Rohdaten."""
    samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(samples**2))
    if rms <= 0:
        return 0.0
    # Relativer Skalenwert (0 bis ~100 dB)
    db = 20 * math.log10(rms / 32768.0) + 90
    return round(db, 1)

def draw_bar(current_db, limit_db, max_scale=100, bar_length=30):
    """Erstellt einen visuellen ASCII-Lärmbalken für das Terminal."""
    scaled_val = int(min(max(current_db, 0), max_scale) / max_scale * bar_length)
    scaled_limit = int(min(max(limit_db, 0), max_scale) / max_scale * bar_length)
    
    bar = ""
    for i in range(bar_length):
        if i < scaled_val:
            if current_db > limit_db:
                bar += "█"  # Alarm
            else:
                bar += "▒"  # Normal
        else:
            if i == scaled_limit:
                bar += "|"  # Limit-Markierung
            else:
                bar += "░"
    return bar

def monitor_zone(zone_name, device_index, db_limit_day, db_limit_night, quiet_start):
    p = pyaudio.PyAudio()
    
    CHUNK = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
    except Exception as e:
        print(f"\n[FEHLER] Konnte Mikrofon/Soundkarte (Index {device_index}) nicht öffnen:")
        print(f"-> {e}\n")
        p.terminate()
        return

    # Statistiken
    max_peak_db = 0.0
    alarm_count = 0
    start_time = time.time()

    # Terminal aufräumen
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        while True:
            # 1. Audiodaten lesen
            data = stream.read(CHUNK, exception_on_overflow=False)
            current_db = calculate_db(data)

            # 2. Peak aktualisieren
            if current_db > max_peak_db:
                max_peak_db = current_db

            # 3. Tageszeit / Limits bestimmen
            now = datetime.datetime.now()
            is_night = now.hour >= quiet_start or now.hour < 6
            current_limit = db_limit_night if is_night else db_limit_day
            mode_str = "NACHTMODUS 🌙" if is_night else "TAGMODUS ☀️"

            # 4. Prüfen ob Alarm vorliegt
            is_alarm = current_db > current_limit
            if is_alarm:
                alarm_count += 1
                status_str = "🚨 ALARM (Zulaut!) 🚨"
            else:
                status_str = "✅ OK (Ruhig)"

            # 5. Balken zeichnen
            bar = draw_bar(current_db, current_limit)

            # 6. Laufzeit berechnen
            elapsed_sec = int(time.time() - start_time)
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_sec))

            # 7. Terminal-Ausgabe (Überschreibt sich selbst sauber)
            output = (
                f"\r============================================================\n"
                f"  STANDALONE LÄRMSCHUTZ | Zone: '{zone_name}'\n"
                f"============================================================\n"
                f" Status:          {status_str}\n"
                f" Modus:           {mode_str} (Nachtruhe ab {quiet_start}:00 Uhr)\n"
                f" Aktueller Pegel: {current_db:5.1f} dB  [{bar}]\n"
                f" Grenzwert:       {current_limit:5.1f} dB\n"
                f"------------------------------------------------------------\n"
                f" Höchster Peak:   {max_peak_db:5.1f} dB\n"
                f" Anz. Alarme:     {alarm_count}\n"
                f" Laufzeit:        {elapsed_str}\n"
                f"============================================================\n"
                f" [Strg+C zum Beenden]\n"
            )

            # Cursor nach oben bewegen & Bild aktualisieren
            sys.stdout.write("\033[H" + output)
            sys.stdout.flush()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nÜberwachung beendet.\n")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def list_audio_devices():
    """Listet alle erkannten Eingangs-Geräte im Terminal auf."""
    p = pyaudio.PyAudio()
    print("\n==================================================")
    print("      VERFÜGBARE AUDIOGERÄTE / MIKROFONE")
    print("==================================================")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev['maxInputChannels'] > 0:
            print(f"  Index [{i}]: {dev['name']}")
    print("==================================================\n")
    p.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unabhängiger Terminal Lärm-Monitor")
    parser.add_argument("--list-devices", action="store_true", help="Listet alle Mikrofon-Indizes auf")
    parser.add_argument("--zone", type=str, default="Partyraum", help="Name der Zone")
    parser.add_argument("--device", type=int, default=None, help="Mikrofon/Soundkarten Index")
    parser.add_argument("--limit-day", type=float, default=DEFAULT_MAX_DB_DAY, help="dB Limit Tagsüber")
    parser.add_argument("--limit-night", type=float, default=DEFAULT_MAX_DB_NIGHT, help="dB Limit Nachts")
    parser.add_argument("--quiet-hour", type=int, default=DEFAULT_QUIET_HOUR_START, help="Stunde für Nachtruhe (z.B. 22)")

    args = parser.parse_args()

    if args.list_devices or args.device is None:
        list_audio_devices()
        print("Starte das Skript mit Angabe deines Mikrofon-Index via --device <ID>:")
        print("Beispiel: python3 decibel_terminal_guard.py --device 1 --zone Partyraum\n")
    else:
        monitor_zone(
            zone_name=args.zone,
            device_index=args.device,
            db_limit_day=args.limit_day,
            db_limit_night=args.limit_night,
            quiet_start=args.quiet_hour
        )
