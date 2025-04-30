#!/bin/bash
set -x

INTERFACE="$1"
OUTPUT_FILE="$2"
TARGET_BSSID="$3"
DURATION="$4"
OLD_CHANNEL="$5"
SECRET="$6"
SCANS_DIR="scans"

if [ -z "$DURATION" ] || [ -z "$SECRET" ] || [ -z "$TARGET_BSSID" ]; then
  echo "Usage: $0 <duration> <sudo-secret> <bssid> [old-channel]"
  exit 1
fi

# Fallback-Werte
if [ -z "$DURATION" ]; then
  DURATION=60
fi

if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="handshake_temp"
fi

OUTPUT_PATH="../$SCANS_DIR/$OUTPUT_FILE"handshake

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

echo "📡 Starte airodump-ng für $DURATION Sekunden – Output: $OUTPUT_PATH"

# 3) Filter-Argumente für airodump-ng bauen
BSSID_ARG="--bssid $TARGET_BSSID"
CHAN_ARG=""
if [ -n "$TARGET_CHANNEL" ]; then
  CHAN_ARG="-c $TARGET_CHANNEL"
fi

UUID=$(uuidgen)
FILENAME="handshake_${TARGET_BSSID//:/}_${UUID}"
FULL_PATH="$SCANS_DIR/$FILENAME.csv"

echo "Ordner: " $FULL_PATH 

echo $SECRET | sudo -S timeout $DURATION \
  airodump-ng --band abg $CHAN_ARG $BSSID_ARG \
    --write-interval 1 \
    -w "$SCANS_DIR/$FILENAME" "$INTERFACE"
