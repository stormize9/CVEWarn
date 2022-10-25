from urllib.request import Request, urlopen
import json 
import requests
import re
import sqlite3
import sys
from bs4 import BeautifulSoup


con = sqlite3.connect('../db/db.db')
cur = con.cursor()

def get_liste_app():
    try:
        REQUETE_AJOUT = "SELECT * FROM Applications NATURAL JOIN applications_installed;"

        cur.execute(REQUETE_AJOUT)
        rows = cur.fetchall()

        
        liste_app = {}
        for line in rows:
            id = line[0]
            app = line[1]
            app = app.lower()
            ver = line[2]
            # host = line[3]
            liste_app[id] = [app,ver]

        return liste_app
        

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()



def get_vendor(product,version):
    product = str(product)
    product_CVE_URL = product
    if len(product_CVE_URL.split())>1:
        first, last = product_CVE_URL.split()
        product_CVE_URL = first+'+'+last
    
    
    url = "https://www.cvedetails.com/product-search.php?vendor_id=0&search="+product_CVE_URL
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find('table', attrs={'class': 'listtable'})
    errormsg = soup.find('td', attrs={'class': 'errormsg'})
    if errormsg is not None:
        product, x2 = product.split()
        url = "https://www.cvedetails.com/product-search.php?vendor_id=0&search="+product
    
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, 'html.parser')

        table = soup.find('table', attrs={'class': 'listtable'})
        errormsg = soup.find('td', attrs={'class': 'errormsg'})
    if errormsg is not None:
        return 0
    else:
        results = table.find_all('tr')

        for result in results:
            data = result.find_all('td')
            if len(data) == 0:
                continue
            vendor = data[2].getText()
            vendor = str(vendor).strip()
            product = product.lower()
            vendor = vendor.lower()
            print(product,"->",vendor)


liste_app = get_liste_app()

if liste_app == None:
    print("No application")
    sys.exit()

for id,[app,ver] in liste_app.items():
    try:
        get_vendor(app,ver)
    except AttributeError as error:
        print(app, "-> erreur")
        continue    
    except ValueError as error:
        print(app, "-> erreur")
        continue
