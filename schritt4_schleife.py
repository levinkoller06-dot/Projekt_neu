# Schritt 4.3: Schleife – Jev macht selbst weiter, bis das Ziel erreicht ist (max. 8 Schritte)
# Benutzung: python schritt4_schleife.py <url> "<ziel>"
# Beispiel:  python schritt4_schleife.py wikipedia.org 'suche nach "Katzen"'
# Text zum Tippen kommt aus dem Ziel: in "Anführungszeichen" oder nach dem Wort "nach".
import os
import re
import sys

from playwright.sync_api import sync_playwright

from schritt2_augen import BRAVE_PFADE, elemente_auslesen, als_liste
from schritt3_gehirn import frage, entscheide, text_modell
from schritt4_web import ziel_url, freigabe

MAX_SCHRITTE = 8


def text_aus_ziel(ziel):
    m = re.search(r'"(.+?)"', ziel) or re.search(r"\bnach\s+(.+)$", ziel, re.I)
    if m:
        return m.group(1).strip()
    # Keine Regel passt: das Text-Modell formuliert den Suchtext
    return text_modell(
        f'Ziel des Nutzers: "{ziel}"\nWas soll in ein Suchfeld getippt werden? '
        "Antworte nur mit dem Suchtext, ohne Anführungszeichen. Wenn kein Text nötig ist, antworte mit -"
    ).strip('" ') or None


def ziel_erreicht(ziel, page, verlauf):
    try:
        inhalt = " ".join(page.inner_text("body").split())[:1200]
    except Exception:
        inhalt = ""
    antwort = frage(
        f"Ziel des Nutzers: {ziel}\nBisherige Schritte: {'; '.join(verlauf)}\n"
        f"Aktuelle Seite: {page.title()} ({page.url})\nSeiteninhalt: {inhalt}",
        "Ist das Ziel auf der aktuellen Seite schon erreicht (Suche zeigt Ergebnisse, gesuchte Seite ist offen)?",
        {"ja": "Ja, das Ziel ist erreicht", "nein": "Nein, es sind noch weitere Schritte nötig"},
    )
    return antwort == "ja"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt4_schleife.py <url> "<ziel>"')
    brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
    if not brave:
        raise SystemExit("Brave nicht gefunden.")
    url, ziel = ziel_url(sys.argv[1]), sys.argv[2]
    text = text_aus_ziel(ziel)
    text = None if text == "-" else text
    print("Text zum Tippen:", text)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave, headless=False)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        getippt = False
        verlauf = []                                        # bisherige Schritte (Element + Seite)
        for schritt in range(1, MAX_SCHRITTE + 1):
            if schritt > 1 and ziel_erreicht(ziel, page, verlauf):   # Prüfen (erst nach dem ersten Schritt)
                print("Ziel erreicht:", page.url)
                break
            elemente = elemente_auslesen(page)                 # Lesen
            if not elemente:
                print("Keine Elemente mehr.")
                break
            liste = als_liste(elemente)
            hinweis = f' Der Text "{text}" ist noch nicht getippt: wähle das Suchfeld (Eingabefeld).' if text and not getippt else ""
            nr = entscheide(f"Ziel: {ziel}. Wähle das Element für den nächsten Schritt.{hinweis}", liste)  # Entscheiden
            ziel_el = elemente[nr - 1]
            print(f"Schritt {schritt}: {liste.splitlines()[nr - 1]}")
            marke = (page.url, liste.splitlines()[nr - 1])
            if verlauf and verlauf[-1] == f"{marke[1]} auf {marke[0]}":   # gleicher Klick auf gleicher Seite = kein Fortschritt
                print("Stopp: kein Fortschritt, das Ziel ist vermutlich erreicht:", page.url)
                break
            verlauf.append(f"{marke[1]} auf {marke[0]}")
            if not freigabe(liste.splitlines()[nr - 1]):
                print("Abgebrochen: nicht freigegeben.")
                break
            sel = f'[data-nr="{nr}"]'
            tippbar = ziel_el["tag"] == "textarea" or (ziel_el["tag"] == "input" and ziel_el["typ"] in ("text", "search", "", "email", "url", "tel"))
            if tippbar and text:
                getippt = True
                page.fill(sel, text)                           # Ausführen
                page.keyboard.press("Enter")
            else:
                try:
                    page.click(sel, timeout=4000)
                except Exception:
                    page.eval_on_selector(sel, "e => e.click()")
            page.wait_for_timeout(2500)
        else:
            print("Abbruch: nach", MAX_SCHRITTE, "Schritten nicht fertig.")
        page.wait_for_timeout(2000)
        browser.close()
