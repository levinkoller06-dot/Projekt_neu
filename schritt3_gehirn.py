# Schritt 3: Gehirn – aus einem Satz entscheidet Jev (TypeSafe, über OpenRouter), welches Element geklickt wird
# Benutzung: python schritt3_gehirn.py "klick auf Anmelden"
import json
import os
import sys
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

from schritt2_augen import BRAVE_PFADE, elemente_auslesen, als_liste

URL = "https://openrouter.ai/api/alpha/decisions"
MODELL = "typesafe/jev-1.13"  # Alternative: "~typesafe/jev-latest"


def key_aus_env_datei():
    datei = Path(__file__).parent / ".env"
    if datei.exists():
        for zeile in datei.read_text(encoding="utf-8").splitlines():
            if zeile.startswith("OPENROUTER_API_KEY="):
                return zeile.split("=", 1)[1].strip()
    return None


def entscheide(befehl, liste_text, anzahl):
    """Der austauschbare Entscheider: gibt die Nummer (1-basiert) des Elements zurück."""
    key = os.environ.get("OPENROUTER_API_KEY") or key_aus_env_datei()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY fehlt (Umgebungsvariable oder .env-Datei).")
    body = {
        "model": MODELL,
        "state": (
            f"Elemente auf der Seite:\n{liste_text}\n\nBefehl des Nutzers: {befehl}\n"
            "Frage: Welche Nummer hat das Element, das laut Befehl bedient werden soll?"
        ),
        "questions": {
            "element": {
                "type": "choice",
                "instructions": "Welches Element soll laut Befehl bedient werden? Antworte mit der Nummer.",
                "criteria": {str(i): z.split(". ", 1)[1] for i, z in enumerate(liste_text.splitlines(), 1)},
            }
        },
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            antwort = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"API-Fehler {e.code}: {e.read().decode(errors='replace')}")
    try:
        a = antwort["answers"]["element"]
        return int(a.get("choice") or a.get("selected"))
    except (KeyError, TypeError, ValueError):
        raise SystemExit(f"Unerwartete Antwort: {antwort}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Benutzung: python schritt3_gehirn.py "klick auf Anmelden"')
    befehl = sys.argv[1]
    brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
    if not brave:
        raise SystemExit("Brave nicht gefunden.")
    testseite = (Path(__file__).parent / "testseite.html").resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave, headless=False)
        page = browser.new_page()
        page.goto(testseite)

        elemente = elemente_auslesen(page)          # Lesen
        liste = als_liste(elemente)
        print(liste)
        nr = entscheide(befehl, liste, len(elemente))  # Entscheiden
        print("Jev wählt:", nr)

        ziel = elemente[nr - 1]                     # Ausführen
        if ziel["id"]:
            page.click("#" + ziel["id"])
        else:
            page.get_by_text(ziel["text"]).first.click()
        print("Status auf der Seite:", page.inner_text("#status"))
        page.wait_for_timeout(4000)
        browser.close()
