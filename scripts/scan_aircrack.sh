#!/bin/bash

INTERFACE="wlan1"
SCANS_DIR="scans"
DURATION="$1"
UUID=$(uuidgen)
FILENAME="scan_$UUID"
FULL_PATH="$SCANS_DIR/$FILENAME.csv"

# Stelle sicher, dass das Scan-Verzeichnis existiert
mkdir -p "$SCANS_DIR"

# Prüfe ob das Interface vorhanden ist
if ! ip link show "$INTERFACE" > /dev/null 2>&1; then
  echo "Interface wlan1 not found"
  exit 1
fi

# Prüfe ob airodump-ng vorhanden ist
if ! command -v airodump-ng &> /dev/null; then
  echo "airodump-ng: not found"
  exit 2
fi

# Prüfe ob das Interface im Monitor-Modus ist
MODE=$(iwconfig "$INTERFACE" 2>/dev/null | grep -o 'Mode:[^ ]*' | cut -d: -f2)
if [ "$MODE" != "Monitor" ]; then
  echo "[i] Setze $INTERFACE in den Monitor-Modus..."
  ip link set "$INTERFACE" down
  iw "$INTERFACE" set monitor control
  ip link set "$INTERFACE" up
fi

# Starte den Scan
echo "[i] Starte airodump-ng für $DURATION Sekunden..."
timeout "$DURATION" airodump-ng --band abg --write-interval 1 --output-format csv -w "$SCANS_DIR/$FILENAME" "$INTERFACE"

# Gib Pfad zurück
if [ -f "$FULL_PATH" ]; then
  echo "Scan abgeschlossen: $FULL_PATH"
else
  echo "Scan abgeschlossen, aber Datei nicht gefunden."
fi
