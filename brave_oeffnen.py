# Öffnet dein normales Brave (mit Steuer-Port) und eine Seite darin.
# Benutzung: python brave_oeffnen.py [adresse]     z.B. python brave_oeffnen.py migros.ch
import sys

from playwright.sync_api import sync_playwright

from schritt2_augen import brave_verbinden

with sync_playwright() as p:
    seite = brave_verbinden(p).new_page()
    seite.goto("https://" + (sys.argv[1] if len(sys.argv) > 1 else "search.brave.com"))
    seite.bring_to_front()
print("Brave ist offen. Melde dich dort an, danach bleibt das Profil gespeichert.")
