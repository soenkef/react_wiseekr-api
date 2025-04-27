#!/usr/bin/env python3
import requests
import time
from requests.exceptions import HTTPError

# URLs der drei IEEE-Listen
URLS = {
    "MA-L": "https://standards-oui.ieee.org/oui/oui.txt",
    "MA-M": "https://standards-oui.ieee.org/oui28/mam.txt",
    "MA-S": "https://standards-oui.ieee.org/oui36/oui36.txt"
}

def fetch_text(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
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
    return None

def strip_header(text: str) -> str:
    """
    Entfernt alles vor der ersten echten Eintragszeile,
    damit beim Zusammenführen keine Duplikate von Kopfzeilen entstehen.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "(base 16)" in line.lower():
            return "\n".join(lines[i:])
    return text

def main():
    merged_lines = []
    for name, url in URLS.items():
        print(f"Lade {name} von {url} …")
        time.sleep(1)  # um die Server nicht zu überlasten
        content = fetch_text(url)
        if not content:
            continue

        body = strip_header(content).splitlines()
        merged_lines.append(f"#### {name}")

        seen_prefixes = set()
        for line in body:
            # Zeilen überspringen, die kein "(base 16)" enthalten
            if "(base 16)" not in line.lower():
                continue

            # Beispiel: "28-6F-B9   (base 16)   Nokia Shanghai Bell Co., Ltd."
            # wir extrahieren "28-6F-B9" als prefix
            parts = line.split("(base 16)")
            prefix = parts[0].strip().lower().replace('-', ':')

            if prefix in seen_prefixes:
                continue
            seen_prefixes.add(prefix)

            merged_lines.append(line)

        merged_lines.append("")  # Leerzeile zwischen Gruppen

    if not merged_lines:
        print("❌ Keine Datei erfolgreich geladen.")
        return

    out_path = "oui_combined.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(merged_lines))

    print(f"✅ Fertig! {len(merged_lines)} Zeilen geschrieben nach {out_path}")


if __name__ == "__main__":
    main()
