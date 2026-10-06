# Schritt 5.2/8: Desktop-Hände – Jev wählt aus einem Satz ein Element in einem Fenster; das Skript klickt, tippt oder drückt Tasten
# Benutzung: python schritt5_aktion.py <fenstertitel-teil> "<befehl>"
# Beispiele: python schritt5_aktion.py Explorer "öffne Downloads"
#            python schritt5_aktion.py Editor 'tippe "Hallo Welt"'
#            python schritt5_aktion.py Editor "drücke strg+s"
#            python schritt5_aktion.py Editor 'tippe "Hallo" ins Textfeld'
import sys

from desktop_befehle import fuer_send_keys, hotkey_zerlegen, ist_riskantes_kuerzel, tipp_text
from schritt3_gehirn import entscheide
from schritt4_web import befehl_zerlegen, freigabe, genauer_treffer


def elemente_mit_objekt(fenster_obj):
    """Wie elemente(), aber mit dem Element selbst: (Art, Name, Objekt)."""
    from schritt5_desktop import ARTEN, MAX, SPALTEN
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


def liste_text(eintraege):
    return "\n".join(f"{i}. {art}: {name}" for i, (art, name, _) in enumerate(eintraege, 1))


def element_ausfuehren(fenster_obj, art, element, text=None):
    """Klickt ein Element (Dateien/Ordner per Doppelklick) oder tippt Text hinein."""
    fenster_obj.set_focus()                                   # nach vorne holen, sonst trifft der Klick ein anderes Fenster
    if text is not None:
        element.set_focus()
        element.type_keys(fuer_send_keys(text), with_spaces=True, set_foreground=False)
    elif art == "Eintrag":
        element.double_click_input()
    else:
        element.click_input()


def aktion_ausfuehren(fenster_obj, befehl):
    """Führt einen Befehl im Fenster aus. Gibt True zurück, wenn etwas ausgeführt wurde."""
    from pywinauto.keyboard import send_keys

    taste = hotkey_zerlegen(befehl)                           # Tastenkürzel: kein Element nötig
    if taste:
        name, keys = taste
        if ist_riskantes_kuerzel(name) and not freigabe(f"Tastenkürzel {name}", immer=True):
            print("Abgebrochen: nicht freigegeben.")
            return False
        fenster_obj.set_focus()
        send_keys(keys)
        print(f"Taste gedrückt: {name}")
        return True

    nur_text = tipp_text(befehl)                              # 'tippe "Text"' ohne Zielfeld: ins aktive Fenster
    if nur_text is not None:
        fenster_obj.set_focus()
        send_keys(fuer_send_keys(nur_text), with_spaces=True)
        print("Text getippt.")
        return True

    eintraege = elemente_mit_objekt(fenster_obj)              # Lesen
    if not eintraege:
        print("Keine bedienbaren Elemente gefunden.")
        return False
    liste = liste_text(eintraege)
    tippen = befehl_zerlegen(befehl)                          # 'tippe X ins Y'
    if tippen:
        nr = entscheide(f"bediene: {tippen[1]}", liste)       # Entscheiden
    else:
        nr = genauer_treffer(befehl.replace("öffne", "klick auf"), liste) or entscheide(befehl, liste)
    art, name, element = eintraege[nr - 1]
    print(f"Jev wählt: {nr}. {art}: {name}")
    if not freigabe(f"{art}: {name}"):
        print("Abgebrochen: nicht freigegeben.")
        return False
    element_ausfuehren(fenster_obj, art, element, tippen[0] if tippen else None)   # Ausführen
    print("Ausgeführt.")
    return True


def fenster_finden(titel):
    from schritt5_desktop import fenster
    ziel = next((w for w in fenster() if titel.lower() in w.window_text().lower()), None)
    if not ziel:
        raise SystemExit(f"Kein Fenster mit '{titel}' gefunden. Offene Fenster: " + ", ".join(w.window_text()[:30] for w in fenster()))
    return ziel


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt5_aktion.py <fenstertitel-teil> "<befehl>"')
    aktion_ausfuehren(fenster_finden(sys.argv[1]), sys.argv[2])
