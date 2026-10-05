# Schritt 5.1: Desktop-Augen (nur Lesen) – offene Fenster und deren Elemente als nummerierte Liste
# Benutzung: python schritt5_desktop.py            -> alle offenen Fenster
#            python schritt5_desktop.py Explorer   -> Elemente des ersten Fensters, dessen Titel "Explorer" enthält
from pywinauto import Desktop

ARTEN = {"Button": "Button", "Edit": "Feld", "ListItem": "Eintrag", "TreeItem": "Ordner", "MenuItem": "Menü",
         "TabItem": "Tab", "CheckBox": "Häkchen", "ComboBox": "Auswahl", "Hyperlink": "Link", "SplitButton": "Button"}
MAX = 60
SPALTEN = {"Name", "Änderungsdatum", "Typ", "Größe"}


def fenster():
    """Alle sichtbaren Fenster mit Titel."""
    return [w for w in Desktop(backend="uia").windows() if w.window_text().strip() and w.is_visible()]


def elemente(fenster_obj):
    """Bedienbare Elemente eines Fensters: (Art, Name)."""
    liste = []
    for e in fenster_obj.descendants():
        art = ARTEN.get(e.element_info.control_type)
        name = " ".join((e.window_text() or "").split())[:60]
        if art == "Feld" and name in SPALTEN:  # Spalten-Unterfelder der Dateiliste weglassen
            continue
        if art and name and e.is_visible():
            liste.append((art, name))
        if len(liste) >= MAX:
            break
    return liste


if __name__ == "__main__":
    import sys
    fl = fenster()
    if len(sys.argv) < 2:
        for i, w in enumerate(fl, 1):
            print(f"{i}. Fenster: {w.window_text()[:70]}")
    else:
        ziel = next((w for w in fl if sys.argv[1].lower() in w.window_text().lower()), None)
        if not ziel:
            raise SystemExit(f"Kein Fenster mit '{sys.argv[1]}' gefunden.")
        print("Fenster:", ziel.window_text())
        for i, (art, name) in enumerate(elemente(ziel), 1):
            print(f"{i}. {art}: {name}")
