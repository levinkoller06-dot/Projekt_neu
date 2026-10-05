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


ABLEHNEN = ("alle ablehnen", "ablehnen", "nur notwendige", "nur erforderliche", "reject all", "decline", "necessary only")


def banner_ablehnen(page):
    """Klickt bei einem Cookie-/Einwilligungsbanner die datensparsamste Option (ablehnen). True, wenn geklickt."""
    elemente = elemente_auslesen(page)
    for i, e in enumerate(elemente, 1):
        name = " ".join((e["text"] or e["label"]).split()).lower()
        if e["tag"] == "button" and any(name == w or name.startswith(w) for w in ABLEHNEN):
            try:
                page.click(f'[data-nr="{i}"]', timeout=3000)
            except Exception:
                page.eval_on_selector(f'[data-nr="{i}"]', "e => e.click()")
            page.wait_for_timeout(1500)
            return True
    return False


def ziel_erreicht(ziel, page, verlauf):
    try:
        inhalt = " ".join(page.inner_text("body").split())[:1200]
    except Exception:
        inhalt = ""
    antwort = frage(
        f"Ziel des Nutzers: {ziel}\nBisherige Schritte: {'; '.join(verlauf)}\n"
        f"Aktuelle Seite: {page.title()} ({page.url})\nSeiteninhalt: {inhalt}",
        "Sind ALLE Teile des Ziels erledigt? Bei 'suche X' müssen Ergebnisse zu X sichtbar sein. "
        "Bei 'klicke ein Ergebnis/einen Link an' muss die Ergebnisseite verlassen und das Ergebnis selbst geöffnet sein.",
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
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass

        getippt = False
        verlauf = []                                        # bisherige Schritte (Element + Seite)
        for schritt in range(1, MAX_SCHRITTE + 1):
            if banner_ablehnen(page):                          # Cookie-/Einwilligungsbanner zuerst ablehnen
                print("Banner abgelehnt.")
            # Erreicht kann das Ziel erst sein, wenn der gesuchte Text auch getippt wurde
            if schritt > 1 and (getippt or not text) and ziel_erreicht(ziel, page, verlauf):
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
            seiten_vorher = len(context.pages)
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
            if len(context.pages) > seiten_vorher:             # Link hat einen neuen Tab geöffnet: dort weitermachen
                page = context.pages[-1]
                page.bring_to_front()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=8000)
                except Exception:
                    pass
        else:
            print("Abbruch: nach", MAX_SCHRITTE, "Schritten nicht fertig.")
        page.wait_for_timeout(2000)
        browser.close()
