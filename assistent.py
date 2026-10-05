# Gemeinsamer Einstieg: ein Satz rein, Jev entscheidet App/Datei (PC) oder Webseite (Browser)
# Benutzung: python assistent.py "öffne spotify"          (ein Befehl)
#            python assistent.py                          (Dauerschleife, Beenden mit leerer Eingabe)
import os
import subprocess
import sys

from schritt3_gehirn import frage, text_modell

HIER = os.path.dirname(os.path.abspath(__file__))


def starte(skript, *args):
    subprocess.run([sys.executable, os.path.join(HIER, skript), *args], cwd=HIER)


def befehl_ausfuehren(satz):
    art = frage(
        f"Befehl des Nutzers: {satz}",
        "Soll ein Programm, eine Datei oder ein Ordner auf dem PC geöffnet werden, oder soll im Browser etwas auf einer Webseite passieren?",
        {
            "pc": "Programm, App, Datei oder Ordner auf dem PC öffnen (z.B. Spotify, Outlook, Downloads, ein Dokument)",
            "web": "Eine Webseite öffnen oder auf einer Webseite etwas tun (z.B. Wikipedia, Suche, Shop, Klicken, Tippen)",
        },
    )
    print("→", "PC" if art == "pc" else "Browser")
    if art == "pc":
        starte("schritt5_oeffnen.py", satz)
        return
    # Browser: Gemini zerlegt den Satz in Webadresse und Ziel
    antwort = text_modell(
        f'Befehl: "{satz}"\nAntworte in genau einer Zeile im Format: ADRESSE | ZIEL\n'
        "ADRESSE = Domain der Webseite (z.B. wikipedia.org, migros.ch). "
        'ZIEL = was auf der Seite getan werden soll, kurz auf Deutsch, Suchbegriff in "Anführungszeichen" '
        '(z.B. suche nach "Katzen"). Wenn die Seite nur geöffnet werden soll, schreibe - als ZIEL.'
    )
    adresse, _, ziel = (t.strip() for t in antwort.splitlines()[0].partition("|"))
    print(f"   Seite: {adresse} | Ziel: {ziel}")
    if ziel in ("", "-"):
        os.startfile("https://" + adresse)
    else:
        starte("schritt4_schleife.py", adresse, ziel)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        befehl_ausfuehren(" ".join(sys.argv[1:]))
    else:
        while True:
            satz = input("Was soll ich tun? ").strip()
            if not satz:
                break
            befehl_ausfuehren(satz)
