# Schritt 1: Hände testen – Brave öffnen und einen Button klicken
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# Brave suchen (normale Installation oder Benutzer-Installation)
BRAVE_PFADE = [
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
]
brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)
if not brave:
    raise SystemExit("Brave nicht gefunden - schick mir, wo brave.exe bei dir liegt.")
print("Starte Brave:", brave)

# Eigene Testseite im gleichen Ordner
testseite = (Path(__file__).parent / "testseite.html").resolve().as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=brave, headless=False)
    page = browser.new_page()
    page.goto(testseite)
    page.wait_for_timeout(2000)              # 2 Sek. schauen: noch nicht geklickt

    page.click("#anmelden")                  # Button "Anmelden" klicken
    print("Status auf der Seite:", page.inner_text("#status"))

    page.wait_for_timeout(4000)              # 4 Sek. Ergebnis anschauen
    browser.close()
