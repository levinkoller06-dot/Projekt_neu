# Stand des Projekts (für neue Claude-Sitzungen)

**Ziel:** Programm, das den PC/Browser per Befehl steuert: Lesen → Entscheiden → Ausführen.

## Plan
1. ✅ Schritt 1 – Hände: Playwright öffnet Brave und klickt einen Button (`schritt1_klick.py`, `testseite.html`)
2. ✅ Schritt 2 – Augen (`schritt2_augen.py`; Testseite hat jetzt Feld, 2 Buttons, Link): Seite auslesen, alle Buttons/Felder als nummerierte Liste ausgeben
3. ✅ Schritt 3 – Gehirn (`schritt3_gehirn.py`, Jev über OpenRouter, Key in lokaler `.env`, nicht im Repo): Modell entscheidet aus einem Satz („klick auf Anmelden“), welches Element geklickt wird

4. ✅ Schritt 4 – Web ausbauen: 4.1 beliebige Seiten (`schritt4_web.py <url|suchbegriff> "<befehl>"`); 4.2 Tippen, mehrere Befehle, Popups; 4.3 Schleife (`schritt4_schleife.py <url> "<ziel>"`, Fortschrittspruefung, Banner ablehnen, neue Tabs, Brave Search); 4.4 Rueckfrage vor riskanten Klicks
5. ✅ Schritt 5 – Desktop: 5.1 Fenster/Explorer lesen (`schritt5_desktop.py`); 5.2 Desktop-Aktion, Explorer oeffnen (`schritt5_aktion.py`); 5.3 Alles per Suche oeffnen, installierte Apps zuerst (`schritt5_oeffnen.py`)
6. ✅ Gemeinsamer Einstieg: `assistent.py` (PC oder Browser)

## Brave
- Normales Brave-Profil, Brave bleibt nach dem Skript offen (CDP)
- Einmalig anmelden: `python brave_oeffnen.py`

## Setup
- Windows, Python 3.12, Playwright 1.63
- Browser: Brave (Pfad wird im Script automatisch gesucht)
- Starten: `python schritt1_klick.py` (Befehle über `python -m ...`, da Scripts-Ordner nicht im PATH)

## Regeln für Claude
- Antworten immer sehr kurz halten (max. ~3 Sätze pro Erklärung)
- Nach jedem Schritt kurz sagen: was gemacht, was es tut
