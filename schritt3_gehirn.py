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


def key_aus_env_datei(name="OPENROUTER_API_KEY"):
    datei = Path(__file__).parent / ".env"
    if datei.exists():
        for zeile in datei.read_text(encoding="utf-8").splitlines():
            if zeile.startswith(name + "="):
                return zeile.split("=", 1)[1].strip()
    return None


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"


def text_modell(aufgabe):
    """Text-Modell (Gemini): erzeugt freien Text, z.B. den Suchbegriff zum Tippen."""
    key = os.environ.get("GOOGLE_API_KEY") or key_aus_env_datei("GOOGLE_API_KEY")
    if not key:
        raise SystemExit("GOOGLE_API_KEY fehlt (Umgebungsvariable oder .env-Datei).")
    body = {
        "contents": [{"parts": [{"text": aufgabe}]}],
        "generationConfig": {"thinkingConfig": {"thinkingBudget": 0}},
    }
    req = urllib.request.Request(
        GEMINI_URL,
        data=json.dumps(body).encode(),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            antwort = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Gemini-Fehler {e.code}: {e.read().decode(errors='replace')}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise SystemExit(f"Gemini nicht erreichbar: {e}")
    try:
        return antwort["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError):
        raise SystemExit(f"Gemini hat keine Antwort geliefert: {antwort}")


def frage(state, instructions, criteria):
    """Der austauschbare Entscheider (Jev): wählt einen Schlüssel aus criteria."""
    key = os.environ.get("OPENROUTER_API_KEY") or key_aus_env_datei()
    if not key:
        raise SystemExit("OPENROUTER_API_KEY fehlt (Umgebungsvariable oder .env-Datei).")
    body = {
        "model": MODELL,
        "state": state,
        "questions": {"frage": {"type": "choice", "instructions": instructions, "criteria": criteria}},
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
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise SystemExit(f"API nicht erreichbar: {e}")
    try:
        a = antwort["answers"]["frage"]
        return str(a.get("choice") or a.get("selected"))
    except (KeyError, TypeError, ValueError):
        raise SystemExit(f"Unerwartete Antwort: {antwort}")


def nummer_pruefen(antwort, anzahl):
    """Wandelt die Modellantwort in eine Nummer von 1 bis anzahl um; sonst klare Fehlermeldung."""
    try:
        nr = int(str(antwort).strip().rstrip("."))
    except ValueError:
        raise SystemExit(f"Ungültige Antwort vom Modell (keine Nummer): {antwort!r}")
    if not 1 <= nr <= anzahl:
        raise SystemExit(f"Ungültige Antwort vom Modell: Nummer {nr} liegt nicht in 1-{anzahl}.")
    return nr


def entscheide(befehl, liste_text, anzahl=None):
    """Gibt die Nummer (1-basiert) des Elements zurück, das der Befehl meint."""
    zeilen = liste_text.splitlines()
    antwort = frage(
        f"Elemente auf der Seite:\n{liste_text}\n\nBefehl des Nutzers: {befehl}",
        "Welches Element soll laut Befehl bedient werden? Antworte mit der Nummer.",
        {str(i): z.split(". ", 1)[1] for i, z in enumerate(zeilen, 1)},
    )
    return nummer_pruefen(antwort, anzahl or len(zeilen))


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
