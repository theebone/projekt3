"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Tibor Nešpor
email: tibornespor97@gmail.com
"""
import argparse
import requests
from bs4 import BeautifulSoup
import os
import csv

# Funkce pro kontrolu, zda je URL platná
def je_platna_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Funkce pro získání obsahu stránky z URL
def ziskej_stranku(url):
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        return None
    return BeautifulSoup(response.content, "html.parser")

# Funkce pro extrakci čísel obcí
def extrahuj_cisla_obci(url):
    soup = ziskej_stranku(url)
    if not soup:
        return []
    
    odkazy = soup.find_all("a", href=True)
    cisla = []
    
    for odkaz in odkazy:
        href = odkaz["href"]
        if "xobec=" in href:
            # Extrahujeme číslo obce z odkazu
            start = href.find("xobec=") + len("xobec=")
            end = href.find('&', start)
            end = end if end != -1 else len(href)
            cislo = href[start:end]
            
            # Kontrolujeme duplicity
            if cislo not in cisla:
                cisla.append(cislo)

    return cisla

# Funkce pro extrakci názvů měst
def extrahuj_nazvy_mest(url):
    soup = ziskej_stranku(url)
    if not soup:
        return []
    
    td_tags = soup.find_all("td", class_="overflow_name")
    mesta = []
    
    for tag in td_tags:
        mesto = tag.text.strip()
        if mesto not in mesta:
            mesta.append(mesto)

    return mesta

# Funkce pro extrakci odkazů na obce
def extrahuj_odkazy_na_obce(url):
    soup = ziskej_stranku(url)
    if not soup:
        return []
    
    odkazy = soup.find_all("a", href=True)
    odkazy_obci = []
    
    for odkaz in odkazy:
        href = odkaz["href"]
        if "ps311" in href and "xobec" in href:
            # Vytvoříme plný odkaz na stránku obce
            plny_odkaz = f"https://www.volby.cz/pls/ps2017nss/{href}"
            if plny_odkaz not in odkazy_obci:
                odkazy_obci.append(plny_odkaz)

    return odkazy_obci

# Funkce pro extrakci volebních dat z odkazů na obce
def extrahuj_volebni_data(odkazy_obci):
    volici = []
    obalky = []
    hlasy = []
    hlasy_stran = {}

    for odkaz in odkazy_obci:
        soup = ziskej_stranku(odkaz)
        if not soup:
            continue
        
        try:
            volici.append(soup.find("td", {"class": "cislo", "headers": "sa2"}).get_text(strip=True) or "")
            obalky.append(soup.find("td", {"class": "cislo", "headers": "sa3"}).get_text(strip=True) or "")
            hlasy.append(soup.find("td", {"class": "cislo", "headers": "sa6"}).get_text(strip=True) or "")
            
            # Extrakce dat o hlasování pro strany
            strany = soup.find_all("td", {"class": "overflow_name", "headers": "t1sa1 t1sb2"})
            hlasy_stran_data = soup.find_all("td", {"class": "cislo", "headers": "t1sa2 t1sb3"})
            
            for strana, hlas in zip(strany, hlasy_stran_data):
                nazev_strany = strana.get_text(strip=True)
                pocet_hlasu = hlas.get_text(strip=True)
                hlasy_stran.setdefault(nazev_strany, []).append(pocet_hlasu)

            # Druhá sada stran
            strany2 = soup.find_all("td", {"class": "overflow_name", "headers": "t2sa1 t2sb2"})
            hlasy2 = soup.find_all("td", {"class": "cislo", "headers": "t2sa2 t2sb3"})
            
            for strana, hlas in zip(strany2, hlasy2):
                nazev_strany = strana.get_text(strip=True)
                pocet_hlasu = hlas.get_text(strip=True)
                hlasy_stran.setdefault(nazev_strany, []).append(pocet_hlasu)

        except Exception as e:
            continue  # Pokud dojde k chybě, pokračujeme na další odkaz

    return volici, obalky, hlasy, hlasy_stran

# Funkce pro uložení dat do CSV souboru
def uloz_data_do_csv(cisla, mesta, volici, obalky, hlasy, hlasy_stran, soubor):
    # Vytvoření adresáře pro soubor, pokud neexistuje
    adresar = os.path.dirname(soubor)
    if adresar and not os.path.exists(adresar):
        os.makedirs(adresar)

    # Seznam stran, pro které budou uloženy hlasy
    nazvy_stran = list(hlasy_stran.keys())
    
    with open(soubor, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Hlavička CSV souboru
        header = ["Číslo obce", "Jméno obce", "Voliči v seznamu", "Vydané obálky", "Platné hlasy"] + nazvy_stran
        writer.writerow(header)

        # Uložení dat pro každou obec
        for i in range(len(cisla)):
            radek = [
                cisla[i],
                mesta[i],
                volici[i],
                obalky[i],
                hlasy[i]
            ]
            radek += [hlasy_stran.get(nazev, [""])[i] for nazev in nazvy_stran]
            writer.writerow(radek)

    print(f"Data byla uložena do souboru {soubor}.")

# Funkce pro kontrolu argumentů
def zkontroluj_argumenty(args):
    if not args.url or not args.csv_jmeno:
        print("Chyba: Musíte zadat URL a název CSV souboru.")
        return False

    if not je_platna_url(args.url):
        print("Chyba: Zadaná URL není platná.")
        return False

    return True

# Hlavní funkce
def main():
    parser = argparse.ArgumentParser(description="Extrahuje volební data z URL a uloží je do CSV.")
    parser.add_argument("url", help="URL volební stránky.")
    parser.add_argument("csv_jmeno", help="Název výstupního CSV souboru.")
    args = parser.parse_args()

    if not zkontroluj_argumenty(args):
        return

    cisla = extrahuj_cisla_obci(args.url)
    mesta = extrahuj_nazvy_mest(args.url)
    odkazy_obci = extrahuj_odkazy_na_obce(args.url)

    if odkazy_obci:
        volici, obalky, hlasy, hlasy_stran = extrahuj_volebni_data(odkazy_obci)
    else:
        volici = obalky = hlasy = []
        hlasy_stran = {}

    uloz_data_do_csv(cisla, mesta, volici, obalky, hlasy, hlasy_stran, args.csv_jmeno)

if __name__ == "__main__":
    main()
