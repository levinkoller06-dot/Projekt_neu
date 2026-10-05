# Schritt 5.3: Alles öffnen – "öffne retrac" sucht Programm, Datei oder Ordner auf dem PC und öffnet es
# Benutzung: python schritt5_oeffnen.py "öffne retrac"
# Es muss kein Explorer-Fenster offen sein. Suchreihenfolge: Startmenü (Programme), dann Benutzerordner, dann Programme-Ordner.
import os
import re
import sys
import time

from schritt3_gehirn import entscheide

ZEITLIMIT = 15  # Sekunden Suche
HOME = os.path.expanduser("~")
STARTMENUE = [
    os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
]
BENUTZERORDNER = [os.path.join(HOME, n) for n in ("Desktop", "Downloads", "Documents", "OneDrive", "Pictures", "Videos", "Music")] + [HOME]
PROGRAMME = [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")]
UEBERSPRINGEN = {"appdata", "node_modules", ".git", ".venv", "__pycache__", "$recycle.bin", "windows", "site-packages"}


def ziel_name(befehl):
    return re.sub(r"^\s*(öffne|oeffne|starte|start|open)\s+(?:den\s+|die\s+|das\s+|mir\s+)?", "", befehl, flags=re.I).strip()


def rang(name, ziel):
    """0 = exakt, 1 = beginnt mit, 2 = enthält, None = passt nicht (Endung wird ignoriert)."""
    stamm = os.path.splitext(name)[0].lower()
    z = ziel.lower()
    if stamm == z or name.lower() == z:
        return 0
    if stamm.startswith(z):
        return 1
    return 2 if z in stamm else None


def suche(ziel):
    """Gibt Treffer als Liste von (rang, pfad) zurück; bricht bei exaktem Treffer sofort ab."""
    start, treffer, gesehen = time.time(), [], set()
    for wurzel in STARTMENUE + BENUTZERORDNER + PROGRAMME:
        if not os.path.isdir(wurzel):
            continue
        tiefe0 = wurzel.rstrip("\\").count("\\")
        for ordner, unterordner, dateien in os.walk(wurzel):
            unterordner[:] = [d for d in unterordner if d.lower() not in UEBERSPRINGEN]
            if wurzel == HOME and ordner.count("\\") - tiefe0 >= 3:   # Benutzerordner nur 3 Ebenen tief
                unterordner[:] = []
            for n in (dateien if wurzel in STARTMENUE else unterordner + dateien):   # im Startmenü nur Programme, keine Ordner
                r = rang(n, ziel)
                pfad = os.path.join(ordner, n)
                if r is not None and pfad not in gesehen:
                    gesehen.add(pfad)
                    treffer.append((r, pfad))
                    if r == 0:
                        return treffer
            if time.time() - start > ZEITLIMIT:
                return treffer
    return treffer


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Benutzung: python schritt5_oeffnen.py "öffne retrac"')
    ziel = ziel_name(sys.argv[1])
    treffer = sorted(suche(ziel), key=lambda t: (t[0], len(t[1])))[:8]
    if not treffer:
        raise SystemExit(f"Nichts gefunden für '{ziel}'.")
    pfad = treffer[0][1]
    if len(treffer) > 1 and treffer[0][0] == treffer[1][0] != 0:      # mehrdeutig: Jev wählt
        liste = "\n".join(f"{i}. Datei: {p}" for i, (_, p) in enumerate(treffer, 1))
        pfad = treffer[entscheide(sys.argv[1], liste) - 1][1]
    print("Öffne:", pfad)
    os.startfile(pfad)
