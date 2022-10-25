from urllib.request import Request, urlopen
import json 
import requests
import re
import sqlite3
import sys
from bs4 import BeautifulSoup


def exceptions(liste_version,version,desc):
    for ver in version:
        ver = ver.strip()
        if ver == '.' or ver == '+' or ver.startswith('802') or ver.startswith('201') or ver.startswith('200') or ver.startswith('202') or ver =='3d' or ver == '365':
            continue
        desc = desc.replace(ver,'')
        liste_version.append(ver)

    return desc


def get_version(desc): #Avoir la ou les versions d'une description

    liste_version = []

    if re.findall('\s*([\d.]+\sto\s[\d.]+)', desc):
        version_to = re.findall('\s*([\d.]+\sto\s[\d.]+)', desc)
        desc = exceptions(liste_version,version_to,desc)
            
    if re.findall('\s*([\d.]+\sthrough\s[\d.]+)', desc):
        version_through = re.findall('\s*([\d.]+\sthrough\s[\d.]+)', desc)
        desc = exceptions(liste_version,version_through,desc)
    
    if re.findall('(before\s[\d.]+)', desc):
        version_before = re.findall('(before\s[\d.]+)', desc)
        desc = exceptions(liste_version,version_before,desc)

    if re.findall('(after\s[\d.]+)', desc):
        version_after = re.findall('(after\s[\d.]+)', desc)
        desc = exceptions(liste_version,version_after,desc)

    if re.findall('(\s[\d.]+)', desc):
        version = re.findall('(\s[\d+\.]+)', desc)
        desc = exceptions(liste_version,version,desc)

    if re.findall('(v[\d.]+)', desc):
        version = re.findall('([\d+\.]+)', desc)
        desc = exceptions(liste_version,version,desc)
    
    if liste_version == []:
        return False
    else:
        return liste_version
  

def get_version_via_cpe(cpe):

    if cpe.startswith("cpe:2.3:a:"):
        cpe = cpe[10:]
        # if re.findall('^[a-zA-Z]+', cpe):
        #     vendor =  re.findall('^[a-zA-Z]+', cpe)
        #     vendor = str(*vendor)
        # if re.findall(':'+'([\d+\.]+)', cpe):
        #     version = re.findall(':'+'([\d+\.]+)', cpe)
        #     version = str(*version)
        cpe_modif = cpe.split(':')
        vendor = cpe_modif[0]
        product = cpe_modif[1]
        version = cpe_modif[2]
        return vendor,product,version
        

def traduction_date(date):
    date = date[:10]
    return date

def update_SQL_sequence():

    try:
        conn = sqlite3.connect('..\..\..\..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        REQUETE_AJOUT = """UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='CVES';"""

        cur.executescript(REQUETE_AJOUT)

        cur.close()
        conn.close()
    except sqlite3.Error as error:
        print("Erreur ajout_bdd_CVE :", error)

def get_id_by_CVE(id):
    try:
        conn = sqlite3.connect('..\..\..\..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        REQUETE_AJOUT = "SELECT id_cve FROM CVES WHERE title = '"+id+"';"

        cur.execute(REQUETE_AJOUT)
        rows = cur.fetchall()

        cur.close()
        conn.close()
        for line in rows:
            return line[0]
        

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()

def ajout_ver_bdd(id,product,ver):
    try:
        id = str(id)
        conn = sqlite3.connect('..\..\..\..\ProjetCyber2\db\db.db')
        REQUETE_AJOUT = """
        INSERT INTO CVES_VER (id_cve, version, application) 
        VALUES (\'"""+id+"""\', \'"""+ver+"""\', \'"""+product+"""\');"""

        cur = conn.cursor()
        cur.execute(REQUETE_AJOUT)
        conn.commit()
        print("Ajout de la version",ver)

        cur.close()
        conn.close()

    except sqlite3.Error as error:
        print("Erreur lors de l'ajout : ", error)



def ajout_bdd(id,product,vendor,date,cvss,summary):
    try:
        conn = sqlite3.connect('..\..\..\..\ProjetCyber2\db\db.db')
        REQUETE_AJOUT = """
        INSERT INTO CVES (title, product, vendor, publication_date, criticality, description) 
        VALUES (\'"""+id+"""\', \'"""+product+"""\', \'"""+vendor+"""\', \'"""+date+"""\', \'"""+cvss+"""\',\'"""+summary+"""\');"""

        cur = conn.cursor()
        cur.execute(REQUETE_AJOUT)
        conn.commit()
        print("Ajout de la CVE",id)

        cur.close()
        conn.close()

    except sqlite3.Error as error:
        print("Erreur lors de l'ajout de la CVE",id,' : ', error)


def requete(vendor_url,product_url):

    url = "https://cvepremium.circl.lu/api/search/"+vendor_url+"/"+product_url

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        result = json.loads(response.text)
        data = result['results']
        total = result['total']

        if total != 0:
            
            for cve in data:
                id = cve['id']
                date = cve['Published']
                date = traduction_date(date)
                cvss = cve['cvss']
                cvss = str(cvss)
                summary = cve['summary']
                summary = summary.replace("'","")
                versions = cve['vulnerable_product']

                # ajout_bdd(id,product_url,vendor_url,date,cvss,summary)
                id_cve = get_id_by_CVE(id)
                for version in versions:
                    if version.startswith("cpe:2.3:a:"):
                        
                        vendor,product,ver = get_version_via_cpe(version)
                        if ver != None:
                            print(id,product,ver)
                            # ajout_ver_bdd(id_cve,product,ver)
                    else:
                        continue
        else:
            print('ERROR application inconnue')
    else: print('ERROR REQUEST : ',response.status_code)



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
            requete(vendor,product)






liste_app = get_liste_app()

for app in liste_app:
    try:
        get_vendor(app)
    except AttributeError as error:
        continue    
    except ValueError as error:
        continue
