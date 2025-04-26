#!/bin/bash
# scan_ap.sh: Scanne Access Points und speichere Ergebnis als CSV
# Usage: ./scan_ap.sh <DURATION_SEC> <SECRET> <OUTFILE_PREFIX>

DURATION=$1       # Dauer des Scans in Sekunden
SECRET=$2         # sudo-Passwort oder Umgebungsvariable
OUTPREFIX=$3      # Dateipräfix für die Ausgabe (ohne .csv)

# Finde das WLAN-Interface (außer loopback)
WIFI_INTERFACE=$(ip link show | grep -v lo | awk -F: '/^[0-9]+:/{print $2}' | head -n1 | tr -d ' ')

if [ -z "$WIFI_INTERFACE" ]; then
  echo "Kein WLAN-Interface gefunden."
  exit 1
fi

# Setze Interface in Monitor-Modus
$SECRET | sudo -S ip link set $WIFI_INTERFACE down
$SECRET | sudo -S iw dev $WIFI_INTERFACE set type monitor
$SECRET | sudo -S ip link set $WIFI_INTERFACE up

# Starte Scan mit Timeout
# Ausgabe im CSV-Format (standard .csv und .kismet.csv)
$SECRET | sudo -S timeout $DURATION \
  airodump-ng --output-format csv --write $OUTPREFIX $WIFI_INTERFACE

# Setze Interface zurück in Managed-Mode
$SECRET | sudo -S ip link set $WIFI_INTERFACE down
$SECRET | sudo -S iw dev $WIFI_INTERFACE set type managed
$SECRET | sudo -S ip link set $WIFI_INTERFACE up

echo "Scan abgeschlossen. CSV-Dateien: ${OUTPREFIX}-01.csv und ${OUTPREFIX}-01.kismet.csv"
