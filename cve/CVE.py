from urllib.request import Request, urlopen
import json 
import requests
import re
import sqlite3
import sys
from bs4 import BeautifulSoup
from main import mydb

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
    mydb.update_CVE_sequence()

def get_id_by_CVE(id):
    rows = mydb.select_id_cve(id)
    for line in rows:
        return line['id_cve']

def ajout_ver_bdd(id,product,ver):
    mydb.insert_cve_version(id,product,ver)


def ajout_bdd(id,date,cvss,summary):
    try:
        mydb.insert_cve(id,date,cvss,summary)
    except sqlite3.IntegrityError as error:
        print("CVE déjà existante")

def requete(vendor_url,product_url,version_product):
    if len(vendor_url.split()) > 1:
        list_word = vendor_url.split()
        vendor_url = ("_".join(list_word))
    
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
                
                ajout_bdd(id,date,cvss,summary)
                id_cve = get_id_by_CVE(id)
                for version in versions:
                    if version.startswith("cpe:2.3:a:"):
                        vendor,product,ver = get_version_via_cpe(version)
                        if ver != version_product:
                            continue
                        if ver == None:
                            continue
                        if ver == '*' or ver == '-':
                            continue
                        if product.startswith(product_url):
                            ajout_ver_bdd(id_cve,product,ver)
                    else:
                        continue




def get_liste_app():
    try:
        rows = mydb.get_list_application()
        liste_app = {}
        for line in rows:
            id = line['id_application']
            app = line['application_name']
            app = app.lower()
            ver = line['application_version']
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
            requete(vendor,product,version)

def ajout_app_vul(id_cve,id_app,id_host):
    try:
        id_cve = str(id_cve)
        id_app = str(id_app)
        mydb.ajout_app_vuln(id_host,id_cve,id_app)
    except sqlite3.Error as error:
        print("Erreur lors de l'ajout de la vulnérabilité",error)


def get_host_id(id_app):
    try:
        
        id_app = str(id_app)
        rows_cve = mydb.get_host_id(id_app)

        list_host = []
        if rows_cve is not None:
            for line in rows_cve:
                id_host = line['id_host']
                list_host.append(id_host)
        return list_host
        
    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()

def correlation(id_app,app,ver):
    try:
        rows_cve = mydb.correlationdb(app,ver)
        if rows_cve is not None:
            list_host = get_host_id(id_app)
            for line in rows_cve:
                id_cve = line['id_cve']
                for host in list_host:
                    ajout_app_vul(id_cve,id_app,host)
        

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()

def main():
    liste_app = get_liste_app()
    if liste_app == None:
        print("No application")
        sys.exit()

    for id,[app,ver] in liste_app.items():
        try:
            ver = re.search('(\d+\.){1,}(\d+)', ver)
            ver = ver.group()
            print(app,ver)
            # update_SQL_sequence()
            get_vendor(app,ver)
            correlation(id,app,ver)
        except AttributeError as error:
            continue    
        except ValueError as error:
            continue
