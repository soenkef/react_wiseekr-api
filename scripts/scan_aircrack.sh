#!/bin/bash


set -x

INTERFACE="wlan1"
SCANS_DIR="scans"
DURATION="$1"
SECRET="$2"
UUID=$(uuidgen)
FILENAME="scan_$UUID"
FULL_PATH="$SCANS_DIR/$FILENAME.csv"

echo "Uebergebene Duration/timeout-Werte: " $DURATION

# Prüfen, ob das Verzeichnis existiert, und bei Bedarf erstellen
if [ ! -d "$SCANS_DIR" ]; then
    mkdir -p "$SCANS_DIR"
    echo "Verzeichnis »$SCANS_DIR« wurde erstellt."
else
    echo "Verzeichnis »$SCANS_DIR« existiert bereits."
fi

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

# kill airodump
echo $SECRET | sudo -S killall airodump-ng
echo $SECRET | sudo -S killall aircrack-ng
echo $SECRET | sudo -S killall airmon-ng

echo $SECRET | sudo -S airmon-ng check kill
echo $SECRET | sudo -S airmon-ng stop "$INTERFACE"

# Prüfe ob das Interface im Monitor-Modus ist
MODE=$(iwconfig "$INTERFACE" 2>/dev/null | grep -o 'Mode:[^ ]*' | cut -d: -f2)
if [ "$MODE" != "Monitor" ]; then
  echo "[i] Setze $INTERFACE in den Monitor-Modus..."
  echo $SECRET | sudo -S ip link set "$INTERFACE" down
  echo $SECRET | sudo -S iw dev "$INTERFACE" set type monitor
  echo $SECRET | sudo -S ip link set "$INTERFACE" up
  echo $SECRET | sudo -S iw dev "$INTERFACE" set power_save off
fi

# Starte den Scan
echo "[i] Starte airodump-ng für $DURATION Sekunden..."
echo $SECRET | sudo -S timeout $DURATION airodump-ng --band abg --write-interval 1 --output-format csv -w "$SCANS_DIR/$FILENAME" "$INTERFACE"

# Gib Pfad zurück
if [ -f "$FULL_PATH" ]; then
  echo "Scan abgeschlossen: $FULL_PATH"
else
  echo "Scan abgeschlossen, aber Datei nicht gefunden."
fi
