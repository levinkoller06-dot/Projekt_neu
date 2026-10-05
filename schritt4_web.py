# Schritt 4.1: Beliebige Webseiten – URL oder Suchbegriff öffnen, Jev wählt das Element, Playwright klickt
# Benutzung: python schritt4_web.py <url oder suchbegriff> "<befehl>"
# Beispiel:  python schritt4_web.py wikipedia.org "klick auf Englisch"
import os
import re
import sys
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from schritt2_augen import BRAVE_PFADE, elemente_auslesen, als_liste
from schritt3_gehirn import entscheide


def befehl_zerlegen(befehl):
    """'tippe Katzen ins Suchfeld' -> ('Katzen', 'Suchfeld'); sonst None."""
    m = re.match(r"\s*tipp\w*\s+(?:\"(.+?)\"|(.+?))\s+(?:in|ins|into)\s+(?:das\s+|die\s+|den\s+)?(.+)", befehl, re.I)
    if not m:
        return None
    return (m.group(1) or m.group(2)).strip(), m.group(3).strip()


RISKANT = ("kaufen", "zahlungspflichtig", "bezahl", "zur kasse", "absenden", "abschicken", "senden",
           "löschen", "entfernen", "buchen", "veröffentlichen", "delete", "buy", "pay", "purchase",
           "checkout", "submit", "send", "bestellung abschliessen", "jetzt bestellen",
           ".exe", ".bat", ".cmd", ".ps1", ".msi", ".vbs", ".scr", ".lnk")  # Programme starten = riskant


def freigabe(eintrag, immer=False):
    """Rückfrage vor riskanten Klicks (kaufen, senden, löschen ...). Ohne Eingabe (kein Terminal) = nein."""
    if not immer and not any(w in eintrag.lower() for w in RISKANT):
        return True
    try:
        return input(f"⚠ Riskante Aktion: «{eintrag}». Ausführen? (ja/nein) ").strip().lower() in ("ja", "j", "yes", "y")
    except EOFError:
        return False


def genauer_treffer(befehl, liste):
    """'klick auf X': gibt es genau ein Element, das exakt X heisst, nimmt man es ohne Jev."""
    m = re.match(r"\s*klick\w*\s+(?:auf\s+)?(?:den\s+|die\s+|das\s+)?(.+)", befehl, re.I)
    if not m:
        return None
    ziel = m.group(1).strip().lower()
    treffer = [i for i, z in enumerate(liste.splitlines(), 1) if z.split(": ", 1)[-1].strip().lower() == ziel]
    return treffer[0] if len(treffer) == 1 else None


def ziel_url(eingabe):
    """URL bleibt URL (https:// wird ergänzt), alles andere wird gesucht."""
    if eingabe.startswith(("http://", "https://", "file://")):
        return eingabe
    if " " not in eingabe and "." in eingabe:
        return "https://" + eingabe
    return "https://search.brave.com/search?q=" + quote_plus(eingabe)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt4_web.py <url oder suchbegriff> "<befehl>"')
    brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
    if not brave:
        raise SystemExit("Brave nicht gefunden.")
    url, befehle = ziel_url(sys.argv[1]), sys.argv[2:]   # mehrere Befehle werden nacheinander ausgeführt

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave, headless=False)
        page = browser.new_page()
        print("Öffne:", url)
        page.goto(url, wait_until="domcontentloaded")
        try:                                             # Seite fertig laden lassen (sonst schliessen sich Popups wieder)
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        page.wait_for_timeout(3000)

        for befehl in befehle:
            print(f"\n=== Befehl: {befehl}")
            elemente = elemente_auslesen(page)           # Lesen
            if not elemente:
                raise SystemExit("Keine bedienbaren Elemente gefunden.")
            liste = als_liste(elemente)
            if os.environ.get("LISTE"):                  # LISTE=1 zeigt, was Jev sieht
                print(liste)
            tippen = befehl_zerlegen(befehl)
            # Entscheiden: bei "tippe X in Y" sucht Jev nur das Ziel Y, der Text X kommt aus dem Satz
            nr = genauer_treffer(befehl, liste) or entscheide(f"bediene: {tippen[1]}" if tippen else befehl, liste)
            print("Jev wählt:", liste.splitlines()[nr - 1])
            if not freigabe(liste.splitlines()[nr - 1]):
                print("Abgebrochen: nicht freigegeben.")
                break

            if tippen:                                   # Ausführen
                page.fill(f'[data-nr="{nr}"]', tippen[0])
                page.keyboard.press("Enter")
            else:
                try:
                    page.click(f'[data-nr="{nr}"]', timeout=5000)
                except Exception:                        # verdeckt/blockiert -> direkter JS-Klick
                    page.eval_on_selector(f'[data-nr="{nr}"]', "e => e.click()")
            page.wait_for_timeout(int(os.environ.get("WARTE", 3500)))
            print("Jetzt auf:", page.url)
            if os.environ.get("LISTE"):
                page.screenshot(path=os.environ["LISTE"] + f"_{befehle.index(befehl) + 1}.png")
        page.wait_for_timeout(5000)
        browser.close()
