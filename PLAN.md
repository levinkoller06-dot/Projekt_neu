# Plan: Nächste Schritte (Projekt_neu) – Schritte 7-10 umgesetzt, noch live auf Windows zu testen

## Context
Schritte 1–6 sind fertig (Web-Schleife, Desktop lesen/öffnen, `assistent.py` als Einstieg). Lücken: keine `requirements.txt`, leere README, dünne Fehlerbehandlung, keine Tests, Desktop kann nur "öffnen" (ohne Rückfrage), kein Gedächtnis zwischen Befehlen.

## Schritte (in dieser Reihenfolge)
1. **Stabilisieren (Schritt 7)**
   - `requirements.txt` (playwright, pywinauto), README ausfüllen (Zweck, Setup, Start), Tippfehler "Jev" in STAND.md prüfen.
   - Fehlerbehandlung: `entscheide()` in `schritt4_schleife.py` (int/Bereich prüfen), `frage()`/`text_modell()` (Timeout, leere `candidates`), `assistent.py` (leere Antwort, Rückgabecode der Subprozesse).
2. **Desktop-Aktionen (Schritt 8)**
   - `schritt5_aktion.py` um Tippen und Hotkeys erweitern, in `assistent.py` als dritte Art "desktop-aktion" einbinden, Rückfrage bei riskanten Aktionen.
3. **Desktop-Schleife (Schritt 9)**
   - Lesen → entscheiden → ausführen → prüfen, analog zu `schritt4_schleife.py`.
4. **Kontext & Tests (Schritt 10)**
   - Browser-Seite/Verlauf über Befehle hinweg behalten.
   - pytest für reine Funktionen (`ziel_name`, `rang`, `text_aus_ziel`), Dry-Run-Modus.
5. `STAND.md` nach jedem Schritt aktualisieren.

## Verifikation
Schritte 7/10: `python -m pytest`, Skripte mit Fehleingaben starten. Schritte 8–9: auf Windows manuell testen (Brave + Explorer), da Desktop-Teil Windows-spezifisch ist.

