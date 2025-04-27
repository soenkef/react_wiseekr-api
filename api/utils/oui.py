import os

OUI_FILE = os.path.join(os.path.dirname(__file__), '../data/oui.txt')

# In-Memory-Cache: Prefix → Vendor
OUI_MAP: dict[str, str] = {}

def load_oui():
    """Liest die OUI-Datei und füllt OUI_MAP einmalig."""
    with open(OUI_FILE, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '(base 16)' in line:
                # z.B. "286FB9     (base 16)\t\tNokia Shanghai Bell Co., Ltd."
                prefix_part, vendor_part = line.split('(base 16)', 1)
                # raw hex: "286fb9"
                key = prefix_part.strip().lower().replace('-', '').replace(':', '')
                # vendor name (alles nach der Base-16-Marker)
                vendor = vendor_part.strip()
                OUI_MAP[key] = vendor

# beim Laden des Moduls registrieren
load_oui()