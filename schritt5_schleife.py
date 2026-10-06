# Schritt 9: Desktop-Schleife – Jev bedient ein Fenster Schritt für Schritt, bis das Ziel erreicht ist (max. 8 Schritte)
# Benutzung: python schritt5_schleife.py <fenstertitel-teil> "<ziel>"
# Beispiel:  python schritt5_schleife.py Editor 'tippe "Hallo Welt" und speichere mit strg+s'
import sys

from schritt3_gehirn import frage
from schritt5_aktion import aktion_ausfuehren, elemente_mit_objekt, fenster_finden, liste_text

MAX_SCHRITTE = 8


def ziel_erreicht(ziel, fenster_obj, verlauf):
    eintraege = elemente_mit_objekt(fenster_obj)
    antwort = frage(
        f"Ziel des Nutzers: {ziel}\nBisherige Schritte: {'; '.join(verlauf)}\n"
        f"Fenster: {fenster_obj.window_text()}\nElemente:\n{liste_text(eintraege)}",
        "Sind ALLE Teile des Ziels erledigt?",
        {"ja": "Ja, das Ziel ist erreicht", "nein": "Nein, es sind noch weitere Schritte nötig"},
    )
    return antwort == "ja"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit('Benutzung: python schritt5_schleife.py <fenstertitel-teil> "<ziel>"')
    from schritt3_gehirn import text_modell
    fenster_obj, ziel = fenster_finden(sys.argv[1]), sys.argv[2]
    verlauf = []
    for schritt in range(1, MAX_SCHRITTE + 1):
        if schritt > 1 and ziel_erreicht(ziel, fenster_obj, verlauf):
            print("Ziel erreicht.")
            break
        liste = liste_text(elemente_mit_objekt(fenster_obj))
        befehl = text_modell(                                   # Entscheiden: ein einzelner Befehl im bekannten Format
            f'Ziel: "{ziel}"\nBisherige Schritte: {"; ".join(verlauf) or "keine"}\nElemente im Fenster:\n{liste}\n\n'
            'Antworte mit genau EINEM nächsten Befehl in einer Zeile, nur in einem dieser Formate: '
            'klick auf <Elementname> | tippe "<Text>" | tippe "<Text>" ins <Feldname> | drücke <Kürzel, z.B. strg+s>. '
            "Wiederhole keinen Schritt, der schon erledigt ist."
        ).splitlines()[0].strip()
        print(f"Schritt {schritt}: {befehl}")
        if befehl in verlauf:                                   # gleicher Schritt zweimal = kein Fortschritt
            print("Stopp: kein Fortschritt.")
            break
        verlauf.append(befehl)
        if not aktion_ausfuehren(fenster_obj, befehl):
            break
    else:
        print("Abbruch: nach", MAX_SCHRITTE, "Schritten nicht fertig.")
