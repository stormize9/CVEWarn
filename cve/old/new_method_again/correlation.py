from urllib.request import Request, urlopen
import json 
import re
import sqlite3
import sys
from bs4 import BeautifulSoup



def get_liste_app():
    try:
        conn = sqlite3.connect('..\..\..\..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        REQUETE_AJOUT = "SELECT * FROM Applications;"

        cur.execute(REQUETE_AJOUT)
        rows = cur.fetchall()

        cur.close()
        conn.close()
        liste_app = []
        for line in rows:
            app = line[1]
            liste_app.append(app)

        return liste_app
        

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()





def get_vendor(product):
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
            print(product,vendor)






liste_app = get_liste_app()

for app in liste_app:
    try:
        get_vendor(app)
    except AttributeError as error:
        continue    
    except ValueError as error:
        continue