Skript pro extrakci volebních dat
Tento skript slouží k extrakci volebních dat z webových stránek a jejich uložení do CSV souboru.

Funkce
Extrahuje čísla obcí, názvy měst a odkazy na obce.
Získává volební data z odkazů na konkrétní obce.
Ukládá získané informace do CSV souboru.
Jak to funguje
Zadání URL: Zadejte URL stránky, ze které chcete získat data.
Generování CSV: Skript stáhne data a uloží je do CSV souboru.
Ověření platnosti: Skript zkontroluje, že URL je správná a že byly zadány všechny argumenty.
Instalace
Nainstalujte potřebné knihovny z readme.txt
Použití
python project3.py https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ&xkraj=0&xobec=1001&xstrana=0&xv=0  vysledky.csv
Poznámky
Skript automaticky ověřuje, že URL je platná. Pokud zadáte špatný nebo neexistující odkaz, upozorní vás na chybu.

