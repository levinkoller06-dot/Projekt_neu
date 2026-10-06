import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistent import zerlege
from desktop_befehle import fuer_send_keys, hotkey_zerlegen, ist_riskantes_kuerzel, tipp_text
from schritt3_gehirn import nummer_pruefen
from schritt4_schleife import text_aus_ziel
from schritt4_web import befehl_zerlegen, freigabe, genauer_treffer, ziel_url
from schritt5_oeffnen import rang, ziel_name


def test_ziel_name_entfernt_verb_und_artikel():
    assert ziel_name("öffne den Spotify") == "Spotify"
    assert ziel_name("starte retrac") == "retrac"


def test_rang():
    assert rang("Spotify.lnk", "spotify") == 0
    assert rang("Spotify Setup", "spotify") == 1
    assert rang("My Spotify", "spotify") == 2
    assert rang("Word", "spotify") is None


def test_text_aus_ziel_regeln():
    assert text_aus_ziel('suche nach "Katzen"') == "Katzen"
    assert text_aus_ziel("suche nach Hunden") == "Hunden"


def test_befehl_zerlegen():
    assert befehl_zerlegen('tippe "Hallo Welt" ins Suchfeld') == ("Hallo Welt", "Suchfeld")
    assert befehl_zerlegen("klick auf OK") is None


def test_genauer_treffer():
    liste = "1. Button: OK\n2. Button: Abbrechen"
    assert genauer_treffer("klick auf OK", liste) == 1
    assert genauer_treffer("klick auf Nein", liste) is None


def test_ziel_url():
    assert ziel_url("wikipedia.org") == "https://wikipedia.org"
    assert ziel_url("katzen bilder").startswith("https://search.brave.com/search?q=")


def test_freigabe(monkeypatch):
    assert freigabe("Button: Weiter") is True
    monkeypatch.setattr("builtins.input", lambda _: "ja")
    assert freigabe("Button: Jetzt kaufen") is True
    monkeypatch.setattr("builtins.input", lambda _: "nein")
    assert freigabe("Button: Jetzt kaufen") is False


def test_nummer_pruefen():
    assert nummer_pruefen("3", 5) == 3
    assert nummer_pruefen(" 2. ", 5) == 2
    for schlecht in ("abc", "0", "9", None):
        with pytest.raises(SystemExit):
            nummer_pruefen(schlecht, 5)


def test_zerlege():
    assert zerlege('wikipedia.org | suche nach "x"') == ("wikipedia.org", 'suche nach "x"')
    assert zerlege("migros.ch | -") == ("migros.ch", "-")
    assert zerlege("") == ("", "")


def test_hotkey():
    assert hotkey_zerlegen("drücke strg+s") == ("strg+s", "^s")
    assert hotkey_zerlegen("drücke f5") == ("f5", "{F5}")
    assert hotkey_zerlegen("drücke strg+") is None
    assert hotkey_zerlegen("drücke strg+unbekannt") is None
    assert hotkey_zerlegen("klick auf OK") is None
    assert ist_riskantes_kuerzel("alt+f4") and not ist_riskantes_kuerzel("strg+s")


def test_tipp_text():
    assert tipp_text('tippe "Hallo Welt"') == "Hallo Welt"
    assert tipp_text('tippe "Hallo" ins Feld') is None
    assert tipp_text("klick auf OK") is None
    assert fuer_send_keys("a+b") == "a{+}b"
