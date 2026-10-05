# Schritt 4.1: Beliebige Webseiten – URL oder Suchbegriff öffnen, Jev wählt das Element, Playwright klickt
# Benutzung: python schritt4_web.py <url oder suchbegriff> "<befehl>"
# Beispiel:  python schritt4_web.py wikipedia.org "klick auf Englisch"
import os
import sys
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from schritt2_augen import BRAVE_PFADE, elemente_auslesen, als_liste
from schritt3_gehirn import entscheide


def ziel_url(eingabe):
    """URL bleibt URL (https:// wird ergänzt), alles andere wird gesucht."""
    if eingabe.startswith(("http://", "https://", "file://")):
        return eingabe
    if " " not in eingabe and "." in eingabe:
        return "https://" + eingabe
    return "https://duckduckgo.com/?q=" + quote_plus(eingabe)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt4_web.py <url oder suchbegriff> "<befehl>"')
    brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
    if not brave:
        raise SystemExit("Brave nicht gefunden.")
    url, befehl = ziel_url(sys.argv[1]), sys.argv[2]

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave, headless=False)
        page = browser.new_page()
        print("Öffne:", url)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)

        elemente = elemente_auslesen(page)               # Lesen
        if not elemente:
            raise SystemExit("Keine bedienbaren Elemente gefunden.")
        liste = als_liste(elemente)
        print(liste)
        nr = entscheide(befehl, liste, len(elemente))    # Entscheiden
        print("Jev wählt:", nr, "->", liste.splitlines()[nr - 1])

        page.click(f'[data-nr="{nr}"]')                  # Ausführen
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(4000)
        print("Jetzt auf:", page.url)
        browser.close()
