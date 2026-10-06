# Gemeinsamer Einstieg: ein Satz rein, Jev entscheidet App/Datei (PC), Fenster bedienen (Desktop) oder Webseite (Browser)
# Benutzung: python assistent.py "öffne spotify"          (ein Befehl)
#            python assistent.py                          (Dauerschleife, Beenden mit leerer Eingabe)
#            python assistent.py --dry-run "öffne spotify" (nur zeigen, was passieren würde, nichts ausführen)
# Der Verlauf der Befehle wird in verlauf.jsonl mitgeschrieben und dem Modell als Kontext mitgegeben.
import json
import os
import subprocess
import sys
import time

from schritt2_augen import BRAVE_PFADE
from schritt3_gehirn import frage, text_modell

HIER = os.path.dirname(os.path.abspath(__file__))
VERLAUF_DATEI = os.path.join(HIER, "verlauf.jsonl")
verlauf = []          # Befehle dieser Sitzung: {"satz", "art", "ziel"}


def starte(skript, *args):
    """Startet ein Teilskript; gibt True zurück, wenn es ohne Fehler endete."""
    ergebnis = subprocess.run([sys.executable, os.path.join(HIER, skript), *args], cwd=HIER)
    if ergebnis.returncode != 0:
        print(f"⚠ {skript} wurde mit Fehler beendet (Code {ergebnis.returncode}).")
    return ergebnis.returncode == 0


def verlauf_text(anzahl=3):
    """Die letzten Befehle als Kontext für das Modell ('klick das erste Ergebnis' bezieht sich auf den Befehl davor)."""
    return "; ".join(f'{v["satz"]} ({v["art"]}: {v["ziel"]})' for v in verlauf[-anzahl:]) or "keine"


def merke(satz, art, ziel):
    eintrag = {"satz": satz, "art": art, "ziel": ziel}
    verlauf.append(eintrag)
    try:
        with open(VERLAUF_DATEI, "a", encoding="utf-8") as f:
            f.write(json.dumps({**eintrag, "zeit": time.strftime("%Y-%m-%d %H:%M:%S")}, ensure_ascii=False) + "\n")
    except OSError:
        pass          # Verlauf ist nur Komfort, kein Grund abzubrechen


def zerlege(antwort):
    """Gemini-Antwort 'LINKS | RECHTS' -> (links, rechts). Leere Antwort ergibt ('', '')."""
    zeilen = antwort.strip().splitlines()
    if not zeilen:
        return "", ""
    links, _, rechts = (t.strip() for t in zeilen[0].partition("|"))
    return links, rechts


def befehl_ausfuehren(satz, trocken=False):
    art = frage(
        f"Befehl des Nutzers: {satz}\nLetzte Befehle: {verlauf_text()}",
        "Soll ein Programm/eine Datei geöffnet werden, ein bereits offenes Programmfenster bedient werden, oder soll im Browser etwas auf einer Webseite passieren?",
        {
            "pc": "Programm, App, Datei oder Ordner auf dem PC öffnen (z.B. Spotify, Outlook, Downloads, ein Dokument)",
            "desktop": "In einem bereits offenen Programmfenster etwas tun (z.B. im Editor tippen, strg+s drücken, im Explorer klicken)",
            "web": "Eine Webseite öffnen oder auf einer Webseite etwas tun (z.B. Wikipedia, Suche, Shop, Klicken, Tippen)",
        },
    )
    print("→", {"pc": "PC", "desktop": "Fenster", "web": "Browser"}.get(art, art))
    if art == "pc":
        merke(satz, art, satz)
        if trocken:
            print("(Trockenlauf) würde öffnen:", satz)
            return
        starte("schritt5_oeffnen.py", satz)
        return
    if art == "desktop":
        fenster, ziel = zerlege(text_modell(
            f'Befehl: "{satz}"\nAntworte in genau einer Zeile im Format: FENSTER | ZIEL\n'
            "FENSTER = ein Teil des Fenstertitels (z.B. Editor, Explorer, Word). ZIEL = was im Fenster getan werden soll, "
            'kurz auf Deutsch, Text in "Anführungszeichen".'
        ))
        if not fenster or not ziel:
            print("Konnte Fenster und Ziel nicht bestimmen.")
            return
        print(f"   Fenster: {fenster} | Ziel: {ziel}")
        merke(satz, art, f"{fenster}: {ziel}")
        if trocken:
            print("(Trockenlauf) würde im Fenster ausführen.")
            return
        starte("schritt5_schleife.py", fenster, ziel)
        return
    # Browser: Gemini zerlegt den Satz in Webadresse und Ziel
    adresse, ziel = zerlege(text_modell(
        f'Befehl: "{satz}"\nLetzte Befehle: {verlauf_text()}\n'
        "Antworte in genau einer Zeile im Format: ADRESSE | ZIEL\n"
        "ADRESSE = Domain der Webseite (z.B. wikipedia.org, migros.ch). Bei einer allgemeinen Websuche ohne genannte Seite "
        "immer search.brave.com, niemals google.com. Bezieht sich der Befehl auf die gerade offene Seite "
        '(z.B. "klick das erste Ergebnis"), schreibe - als ADRESSE. '
        'ZIEL = was auf der Seite getan werden soll, kurz auf Deutsch, Suchbegriff in "Anführungszeichen" '
        '(z.B. suche nach "Katzen"). Wenn die Seite nur geöffnet werden soll, schreibe - als ZIEL.'
    ))
    if not adresse:
        print("Konnte keine Webadresse bestimmen.")
        return
    print(f"   Seite: {adresse} | Ziel: {ziel}")
    merke(satz, art, f"{adresse}: {ziel}")
    if trocken:
        print("(Trockenlauf) würde im Browser ausführen.")
        return
    if ziel in ("", "-"):
        if adresse == "-":
            print("Nichts zu tun.")
            return
        brave = next((p for p in BRAVE_PFADE if os.path.exists(p)), None)   # immer Brave, nie der Standardbrowser
        subprocess.Popen([brave, "https://" + adresse]) if brave else os.startfile("https://" + adresse)
    else:
        starte("schritt4_schleife.py", adresse, ziel)      # Adresse "-" = aktuelle Seite weiterbenutzen


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    trocken = "--dry-run" in sys.argv[1:]
    if args:
        befehl_ausfuehren(" ".join(args), trocken)
    else:
        while True:
            satz = input("Was soll ich tun? ").strip()
            if not satz:
                break
            befehl_ausfuehren(satz, trocken)
