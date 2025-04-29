#!/bin/bash

INTERFACE="wlan0"
SCANS_DIR="scans"
DURATION="$1"              # 1. Parameter: Dauer in Sekunden
SECRET="$2"                # 2. Parameter: Dein sudo-Passwort
TARGET_BSSID="$3"          # 3. Parameter: MAC-Adresse des AP
OLD_CHANNEL="$4"           # 4. Parameter: zuvor bekannter Kanal (optional)

if [ -z "$DURATION" ] || [ -z "$SECRET" ] || [ -z "$TARGET_BSSID" ]; then
  echo "Usage: $0 <duration> <sudo-secret> <bssid> [old-channel]"
  exit 1
fi

mkdir -p "$SCANS_DIR"

# 1) Interface prüfen und in Monitor-Modus schalten
if ! ip link show "$INTERFACE" &>/dev/null; then
  echo "Interface $INTERFACE not found"
  exit 1
fi

echo $SECRET | sudo -S airmon-ng check kill
echo $SECRET | sudo -S airmon-ng stop "$INTERFACE"

MODE=$(iwconfig "$INTERFACE" 2>/dev/null | grep -o 'Mode:[^ ]*' | cut -d: -f2)
if [ "$MODE" != "Monitor" ]; then
  echo "[i] Setze $INTERFACE in Monitor-Modus..."
  echo $SECRET | sudo -S ip link set "$INTERFACE" down
  echo $SECRET | sudo -S iw dev "$INTERFACE" set type monitor
  echo $SECRET | sudo -S ip link set "$INTERFACE" up
  echo $SECRET | sudo -S iw dev "$INTERFACE" set power_save off
fi

# 2) Aktuellen Kanal ermitteln
echo "[i] Ermittle aktuellen Kanal für BSSID $TARGET_BSSID ..."
# iw scan verlangt manchmal managed mode; wir nutzen monitor mode scan:
CHAN_DETECTED=$(sudo iw dev "$INTERFACE" scan ap "$TARGET_BSSID" 2>/dev/null \
  | grep -m1 "DS Parameter set:" \
  | awk '{print $4}')

if [ -n "$CHAN_DETECTED" ]; then
  TARGET_CHANNEL="$CHAN_DETECTED"
  echo "[i] Gefundener Kanal: $TARGET_CHANNEL"
else
  if [ -n "$OLD_CHANNEL" ]; then
    TARGET_CHANNEL="$OLD_CHANNEL"
    echo "[!] Kanal konnte nicht ermittelt, verwende übergebenen Kanal: $TARGET_CHANNEL"
  else
    TARGET_CHANNEL=""
    echo "[!] Kanal konnte nicht ermittelt und keiner übergeben – scanne kanal-hopping"
  fi
fi

# 3) Filter-Argumente für airodump-ng bauen
BSSID_ARG="--bssid $TARGET_BSSID"
CHAN_ARG=""
if [ -n "$TARGET_CHANNEL" ]; then
  CHAN_ARG="-c $TARGET_CHANNEL"
fi

UUID=$(uuidgen)
FILENAME="scan_${TARGET_BSSID//:/}_${UUID}"
FULL_PATH="$SCANS_DIR/$FILENAME.csv"

echo "Ordner: " $FULL_PATH 

# 4) Airodump-ng starten
echo "[i] Scanne BSSID $TARGET_BSSID auf Kanal ${TARGET_CHANNEL:-all} für $DURATION s ..."
echo $SECRET | sudo -S timeout $DURATION \
  airodump-ng --band abg $CHAN_ARG $BSSID_ARG \
    --write-interval 1 --output-format csv \
    -w "$SCANS_DIR/$FILENAME" "$INTERFACE"

# 5) Ergebnis ausgeben 
if [ -f "$FULL_PATH" ]; then
  echo "Scan abgeschlossen: $FULL_PATH"
else
  echo "Scan beendet, aber $FULL_PATH nicht gefunden." 
fi
