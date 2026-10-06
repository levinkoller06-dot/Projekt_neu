# Reine Hilfsfunktionen für Desktop-Befehle (Tippen, Tastenkürzel) – ohne pywinauto, daher überall testbar
import re

TASTEN = {"strg": "^", "ctrl": "^", "alt": "%", "umschalt": "+", "shift": "+",
          "enter": "{ENTER}", "return": "{ENTER}", "esc": "{ESC}", "escape": "{ESC}", "tab": "{TAB}",
          "entf": "{DELETE}", "delete": "{DELETE}", "leertaste": "{SPACE}", "space": "{SPACE}",
          "backspace": "{BACKSPACE}", "pos1": "{HOME}", "home": "{HOME}", "ende": "{END}", "end": "{END}",
          "oben": "{UP}", "unten": "{DOWN}", "links": "{LEFT}", "rechts": "{RIGHT}"}
MODIFIER = {"^", "%", "+"}
RISKANTE_KUERZEL = {"alt+f4", "entf", "delete", "strg+entf", "ctrl+delete", "umschalt+entf", "shift+delete",
                    "strg+w", "ctrl+w", "strg+q", "ctrl+q"}   # schliessen/löschen


def hotkey_zerlegen(befehl):
    """'drücke strg+s' -> ('strg+s', '^s') im Format von pywinauto.send_keys; sonst None."""
    m = re.match(r"\s*(?:dr(?:ü|ue|u)cke|druecke|press|hotkey|tastenkürzel)\s+(?:die\s+)?(?:taste\s+)?(\S+)\s*$", befehl, re.I)
    if not m:
        return None
    teile = [t.lower() for t in m.group(1).split("+") if t]
    if not teile:
        return None
    ergebnis = ""
    for t in teile:
        if t in TASTEN:
            ergebnis += TASTEN[t]
        elif re.fullmatch(r"f([1-9]|1[0-2])", t):
            ergebnis += "{" + t.upper() + "}"
        elif len(t) == 1:
            ergebnis += t
        else:
            return None                                   # unbekannte Taste: lieber nichts tun als Falsches
    if ergebnis and ergebnis[-1] in MODIFIER:             # Kürzel muss mit einer echten Taste enden
        return None
    return "+".join(teile), ergebnis


def ist_riskantes_kuerzel(name):
    return name.lower() in RISKANTE_KUERZEL


def tipp_text(befehl):
    """'tippe "Hallo Welt"' -> 'Hallo Welt' (ohne Zielfeld); sonst None."""
    m = re.match(r"\s*(?:tipp\w*|schreib\w*)\s+(?:\"(.+?)\"|(.+?))\s*$", befehl, re.I)
    if not m or re.search(r"\s(?:in|ins|into)\s", m.group(2) or "", re.I):
        return None
    return (m.group(1) or m.group(2)).strip()


def fuer_send_keys(text):
    """Sonderzeichen von pywinauto.send_keys schützen, damit Text wörtlich getippt wird."""
    return "".join("{" + c + "}" if c in "+^%~(){}[]" else c for c in text)
