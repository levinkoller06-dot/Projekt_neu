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
() => {
  document.querySelectorAll('[data-nr]').forEach(e => e.removeAttribute('data-nr'));  // alte Nummern löschen
  const sel = 'button, a[href], input, textarea, select, [role=button], [role=option], mat-option';
  // Nur Elemente, die man wirklich anklicken kann: sichtbar und nicht von einem Popup verdeckt
  const klickbar = e => {
    if (e.type === 'hidden' || !e.checkVisibility({checkVisibilityCSS: true, checkOpacity: e.type !== 'radio' && e.type !== 'checkbox'}) || !e.getClientRects().length) return false;
    if (e.closest('[inert], [aria-hidden=true]')) return false;  // Seite hinter einem offenen Popup
    const r = e.getBoundingClientRect();
    const x = r.left + r.width / 2, y = r.top + r.height / 2;
    if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) return true;  // ausserhalb des Bildes: nicht prüfbar
    const hit = document.elementFromPoint(x, y);
    if (!hit) return false;
    if (e.contains(hit) || hit.contains(e)) return true;
    const box = e.closest('label, mat-radio-button, mat-button-toggle, [role=radiogroup]');  // Radio-Buttons liegen hinter ihrem Label
    return !!box && box.contains(hit);
  };
  return [...document.querySelectorAll(sel)].filter(klickbar)
  .slice(0, 60)
  .map((e, i) => (e.setAttribute('data-nr', i + 1), {
    tag: e.tagName.toLowerCase(),
    typ: e.type || '',
    text: (e.innerText || e.value || '').trim(),
    platzhalter: e.placeholder || '',
    id: e.id || '',
    label: e.getAttribute('aria-label') || e.title || '',
    href: (e.getAttribute('href') || '').slice(0, 60),
  }));
}
"""


def elemente_auslesen(page):
    return page.evaluate(SAMMELN)


def als_liste(elemente):
    zeilen = []
    for i, e in enumerate(elemente, 1):
        art = {"button": "Button", "a": "Link", "input": "Feld", "textarea": "Feld", "select": "Auswahl", "mat-option": "Vorschlag"}.get(e["tag"], e["tag"])
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
