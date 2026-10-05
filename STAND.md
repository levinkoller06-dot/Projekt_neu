# Stand des Projekts (für neue Claude-Sitzungen)

**Ziel:** Programm, das den PC/Browser per Befehl steuert: Lesen → Entscheiden → Ausführen.

## Plan
1. ✅ Schritt 1 – Hände: Playwright öffnet Brave und klickt einen Button (`schritt1_klick.py`, `testseite.html`)
2. ✅ Schritt 2 – Augen (`schritt2_augen.py`; Testseite hat jetzt Feld, 2 Buttons, Link): Seite auslesen, alle Buttons/Felder als nummerierte Liste ausgeben
3. ✅ Schritt 3 – Gehirn (`schritt3_gehirn.py`, Jev über OpenRouter, Key in lokaler `.env`, nicht im Repo): Modell entscheidet aus einem Satz („klick auf Anmelden“), welches Element geklickt wird

## Setup
- Windows, Python 3.12, Playwright 1.63
- Browser: Brave (Pfad wird im Script automatisch gesucht)
- Starten: `python schritt1_klick.py` (Befehle über `python -m ...`, da Scripts-Ordner nicht im PATH)

## Regeln für Claude
- Antworten immer sehr kurz halten (max. ~3 Sätze pro Erklärung)
- Nach jedem Schritt kurz sagen: was gemacht, was es tut
