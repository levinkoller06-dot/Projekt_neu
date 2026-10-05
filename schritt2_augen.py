# Schritt 2: Augen – Seite auslesen und alle Buttons/Felder/Links als nummerierte Liste ausgeben
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BRAVE_PFADE = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
]

# JS im Browser: sichtbare, bedienbare Elemente einsammeln
SAMMELN = """
() => [...document.querySelectorAll('button, a[href], input, textarea, select, [role=button]')]
  .filter(e => e.offsetParent !== null && e.type !== 'hidden')
  .slice(0, 60)
  .map((e, i) => (e.setAttribute('data-nr', i + 1), {
    tag: e.tagName.toLowerCase(),
    typ: e.type || '',
    text: (e.innerText || e.value || '').trim(),
    platzhalter: e.placeholder || '',
    id: e.id || '',
    label: e.getAttribute('aria-label') || e.title || '',
    href: (e.getAttribute('href') || '').slice(0, 60),
  }))
"""


def elemente_auslesen(page):
    return page.evaluate(SAMMELN)


def als_liste(elemente):
    zeilen = []
    for i, e in enumerate(elemente, 1):
        art = {"button": "Button", "a": "Link", "input": "Feld", "textarea": "Feld", "select": "Auswahl"}.get(e["tag"], e["tag"])
        name = e["text"] or e["platzhalter"] or e["label"] or e["id"] or e["href"] or "(ohne Name)"
        name = " ".join(name.split())[:60]  # eine Zeile, max. 60 Zeichen
        zeilen.append(f"{i}. {art}: {name}")
    return "\n".join(zeilen)


if __name__ == "__main__":
    brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
    if not brave:
        raise SystemExit("Brave nicht gefunden.")
    ziel = sys.argv[1] if len(sys.argv) > 1 else (Path(__file__).parent / "testseite.html").resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave, headless=True)
        page = browser.new_page()
        page.goto(ziel)
        print(als_liste(elemente_auslesen(page)))
        browser.close()
