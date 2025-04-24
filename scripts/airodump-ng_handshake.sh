#!/bin/bash
set -x

INTERFACE="$1"
OUTPUT_FILE="$2"
DURATION="$3"

# Fallback-Werte
if [ -z "$DURATION" ]; then
  DURATION=60
fi

if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="handshake_temp"
fi

OUTPUT_PATH="../scans/$OUTPUT_FILE"

echo "📡 Starte airodump-ng für $DURATION Sekunden – Output: $OUTPUT_PATH"
timeout "$DURATION" airodump-ng --write "$OUTPUT_PATH" --write-interval 1 --output-format cap "$INTERFACE"
