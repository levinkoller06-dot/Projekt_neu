# Stand des Projekts (fÃ¼r neue Claude-Sitzungen)

**Ziel:** Programm, das den PC/Browser per Befehl steuert: Lesen â†’ Entscheiden â†’ AusfÃ¼hren.

## Plan
1. âœ… Schritt 1 â€“ HÃ¤nde: Playwright Ã¶ffnet Brave und klickt einen Button (`schritt1_klick.py`, `testseite.html`)
2. âœ… Schritt 2 â€“ Augen (`schritt2_augen.py`; Testseite hat jetzt Feld, 2 Buttons, Link): Seite auslesen, alle Buttons/Felder als nummerierte Liste ausgeben
3. âœ… Schritt 3 â€“ Gehirn (`schritt3_gehirn.py`, Jev Ã¼ber OpenRouter, Key in lokaler `.env`, nicht im Repo): Modell entscheidet aus einem Satz (â€žklick auf Anmeldenâ€œ), welches Element geklickt wird

4. â³ Schritt 4 â€“ Web ausbauen: 4.1 âœ… beliebige Seiten (`schritt4_web.py <url|suchbegriff> "<befehl>"`); 4.2 Tippen; 4.3 ✅ Schleife (`schritt4_schleife.py <url> "<ziel>"`)
5. â³ Schritt 5 â€“ Desktop/Explorer (UI Automation, erst nur Lesen)

## Setup
- Windows, Python 3.12, Playwright 1.63
- Browser: Brave (Pfad wird im Script automatisch gesucht)
- Starten: `python schritt1_klick.py` (Befehle Ã¼ber `python -m ...`, da Scripts-Ordner nicht im PATH)

## Regeln fÃ¼r Claude
- Antworten immer sehr kurz halten (max. ~3 SÃ¤tze pro ErklÃ¤rung)
- Nach jedem Schritt kurz sagen: was gemacht, was es tut

