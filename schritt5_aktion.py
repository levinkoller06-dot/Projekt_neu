# Schritt 5.2: Desktop-Hände – Jev wählt aus einem Satz ein Element in einem Fenster, das Skript öffnet/klickt es
# Benutzung: python schritt5_aktion.py <fenstertitel-teil> "<befehl>"
# Beispiel:  python schritt5_aktion.py Explorer "öffne Downloads"
import sys

from schritt5_desktop import ARTEN, MAX, SPALTEN, fenster
from schritt3_gehirn import entscheide
from schritt4_web import genauer_treffer


def elemente_mit_objekt(fenster_obj):
    """Wie elemente(), aber mit dem Element selbst: (Art, Name, Objekt)."""
    liste = []
    for e in fenster_obj.descendants():
        art = ARTEN.get(e.element_info.control_type)
        name = " ".join((e.window_text() or "").split())[:60]
        if art == "Feld" and name in SPALTEN:
            continue
        if art and name and e.is_visible():
            liste.append((art, name, e))
        if len(liste) >= MAX:
            break
    return liste


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt5_aktion.py <fenstertitel-teil> "<befehl>"')
    titel, befehl = sys.argv[1], sys.argv[2]
    ziel = next((w for w in fenster() if titel.lower() in w.window_text().lower()), None)
    if not ziel:
        raise SystemExit(f"Kein Fenster mit '{titel}' gefunden. Offene Fenster: " + ", ".join(w.window_text()[:30] for w in fenster()))

    eintraege = elemente_mit_objekt(ziel)                       # Lesen
    liste = "\n".join(f"{i}. {art}: {name}" for i, (art, name, _) in enumerate(eintraege, 1))
    nr = genauer_treffer(befehl.replace("öffne", "klick auf"), liste) or entscheide(befehl, liste)  # Entscheiden
    art, name, element = eintraege[nr - 1]
    print(f"Jev wählt: {nr}. {art}: {name}")

    ziel.set_focus()                                            # nach vorne holen, sonst trifft der Klick ein anderes Fenster
    if art == "Eintrag":                                      # Ausführen: Dateien/Ordner in der Liste per Doppelklick
        element.double_click_input()
    else:
        element.click_input()
    print("Ausgeführt.")
