# Projekt_neu – PC und Browser per Satz steuern

Ein Satz rein, das Programm entscheidet und führt aus: Lesen → Entscheiden (Modell) → Ausführen.
Windows, Python 3.12+, Brave-Browser.

## Setup
1. `pip install -r requirements.txt` (Playwright, pywinauto, pytest)
2. Datei `.env` anlegen (nicht im Repo) mit `OPENROUTER_API_KEY=...` (Entscheider) und `GOOGLE_API_KEY=...` (Textmodell)
3. Einmalig `python brave_oeffnen.py` und in Brave anmelden (normales Profil, Brave bleibt offen)

## Benutzung
```
python assistent.py "öffne spotify"            # ein Befehl
python assistent.py                            # Dauerschleife, leere Eingabe beendet
python assistent.py --dry-run "öffne spotify"  # nur anzeigen, nichts ausführen
```
Was geht:
- **PC:** Programme, Apps, Dateien und Ordner per Suche öffnen (`schritt5_oeffnen.py`)
- **Fenster:** in offenen Programmen klicken, tippen, Tastenkürzel drücken (`schritt5_aktion.py`, mehrstufig `schritt5_schleife.py`)
- **Browser:** Webseiten öffnen, suchen, klicken, tippen, mehrere Schritte (`schritt4_schleife.py`); "klick das erste Ergebnis" arbeitet auf der zuletzt offenen Seite weiter
- Rückfrage vor riskanten Aktionen (kaufen, senden, löschen, Programme starten, Alt+F4 …)
- Verlauf aller Befehle in `verlauf.jsonl` (lokal, nicht im Repo)

## Tests
`python -m pytest` (reine Funktionen, braucht kein Windows und keine API-Keys)

Stand und Plan: `STAND.md`, `PLAN.md`
