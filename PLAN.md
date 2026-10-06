# Plan: Nächste Schritte (Projekt_neu)

## Context
Schritte 1–6 sind fertig (Web-Schleife, Desktop lesen/öffnen, `assistent.py` als Einstieg). Lücken: keine `requirements.txt`, leere README, dünne Fehlerbehandlung, keine Tests, Desktop kann nur "öffnen" (ohne Rückfrage), kein Gedächtnis zwischen Befehlen.

## Schritte (in dieser Reihenfolge)
1. **Stabilisieren (Schritt 7)**
   - `requirements.txt` (playwright, pywinauto), README ausfüllen (Zweck, Setup, Start), Tippfehler "Jev" in STAND.md prüfen.
   - Fehlerbehandlung: `entscheide()` in `schritt4_schleife.py` (int/Bereich prüfen), `frage()`/`text_modell()` (Timeout, leere `candidates`), `assistent.py` (leere Antwort, Rückgabecode der Subprozesse).
2. **Sicherheit Desktop (Schritt 8)**
   - Rückfrage (`freigabe`-Muster aus der Web-Schleife) vor dem Öffnen mehrdeutiger Treffer in `schritt5_oeffnen.py`.
3. **Desktop-Aktionen (Schritt 9)**
   - `schritt5_aktion.py` um Tippen und Hotkeys erweitern, in `assistent.py` als dritte Art "desktop-aktion" einbinden, Rückfrage bei riskanten Aktionen.
4. **Desktop-Schleife (Schritt 10)**
   - Lesen → entscheiden → ausführen → prüfen, analog zu `schritt4_schleife.py`.
5. **Kontext & Tests (Schritt 11)**
   - Browser-Seite/Verlauf über Befehle hinweg behalten.
   - pytest für reine Funktionen (`ziel_name`, `rang`, `text_aus_ziel`), Dry-Run-Modus.
6. `STAND.md` nach jedem Schritt aktualisieren.

## Verifikation
Schritte 1/5/6: `python -m pytest`, Skripte mit Fehleingaben starten. Schritte 2–4: auf Windows manuell testen (Brave + Explorer), da Desktop-Teil Windows-spezifisch ist.

