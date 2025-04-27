#!/usr/bin/env python3
import requests
import time
import re
from requests.exceptions import HTTPError

# URLs der drei IEEE-Listen
URLS = {
    "MA-L": "https://standards-oui.ieee.org/oui/oui.txt",
    "MA-M": "https://standards-oui.ieee.org/oui28/mam.txt",
    "MA-S": "https://standards-oui.ieee.org/oui36/oui36.txt"
}

# Regex für einzelne OUI-Einträge im 6-stelligen Hex-Format ohne Bereich
OUI_ENTRY_RE = re.compile(r"^\s*([0-9A-F]{6})\s+\(base 16\)\s+(.*)$", re.IGNORECASE)


def fetch_text(url: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()
        return resp.text
    except HTTPError as e:
        print(f"⚠️ HTTP-Fehler {e.response.status_code} beim Laden von {url}, überspringe…")
        return ""
    except Exception as e:
        print(f"⚠️ Fehler beim Laden von {url}: {e}")
        return ""


def strip_header(text: str) -> str:
    """
    Entfernt alles vor der ersten Zeile mit '(base 16)'.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if '(base 16)' in line.lower():
            return "\n".join(lines[i:])
    return text


def main():
    results = []
    seen = set()

    for name, url in URLS.items():
        print(f"Lade {name} von {url} …")
        time.sleep(1)
        content = fetch_text(url)
        if not content:
            continue

        body = strip_header(content).splitlines()

        # Durchsuche jede Zeile und filtere nur 6-stellige Hex-OUI-Einträge (keine Bereiche)
        for line in body:
            match = OUI_ENTRY_RE.match(line)
            if not match:
                continue
            prefix = match.group(1).upper()
            vendor = match.group(2).strip()

            if prefix in seen:
                continue
            seen.add(prefix)

            results.append(f"{prefix}   (base 16)    {vendor}")

    if not results:
        print("❌ Keine passenden OUI-Einträge gefunden.")
        return

    out_file = "../api/data/oui_combined.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"✅ Fertig! {len(results)} Einträge geschrieben nach {out_file}")


if __name__ == "__main__":
    main()
