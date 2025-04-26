import os

OUI_FILE = os.path.join(os.path.dirname(__file__), '../data/oui.txt')

# In-Memory-Cache: Prefix → Vendor
OUI_MAP: dict[str, str] = {}

def load_oui():
    """Liest die OUI-Datei und füllt OUI_MAP einmalig."""
    with open(OUI_FILE, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '(base 16)' in line:
                prefix, vendor = line.split('(base 16)')
                # formatiere z. B. '00-1A-2B' → '00:1a:2b'
                key = prefix.strip().lower().replace('-', ':')
                OUI_MAP[key] = vendor.strip()

# Ruf load_oui() beim Modul-Import auf
load_oui()
