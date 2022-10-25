from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import datetime
import sqlite3
import sys
import re
from packaging import version
from flask import scaffold
from CVE_github import *



site = 'https://www.cvedetails.com/'

now = datetime.datetime.now()
current_year = '{:02d}'.format(now.year)
month = '{:02d}'.format(now.month)
day = '{:02d}'.format(now.day)
hour = '{:02d}'.format(now.hour)
minute = '{:02d}'.format(now.minute)
current_date = '{}-{}-{}'.format(current_year, month, day)

current_year_int = int(current_year)
date_limite = '{}-{}-{}'.format(current_year_int-5, month, day)
annee_limite = current_year_int-5



def postdate(limit_date, date_CVE):
    date1 = limit_date.split('-')
    date2 = date_CVE.split('-')
    if int(date2[0])>int(date1[0]):
        return True
    elif int(date2[0])==int(date1[0]):
        if int(date2[1])>int(date1[1]):
            return True
        elif int(date2[1])==int(date1[1]):
            if int(date2[2])>=int(date1[2]):
                return True
    return False
    



def description_cve(CVE):
    url = "https://cve.mitre.org/cgi-bin/cvename.cgi?name="+CVE

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    results = soup.find_all('div',  {'id': 'GeneratedTable'})

    for result in results:
        data = result.find_all('td')
        if len(data) == 0:
            continue
        try:
            desc = data[2].getText()
            desc = str(desc).strip()
        except IndexError:
            CVE = 'null'
    return desc





def get_idApp_by_name(application):
    try:
        conn = sqlite3.connect('..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        REQUETE_AJOUT = """Select IDApplication
                        From Applications
                        Where NomApplication = \'"""+application+"""\';"""


        cur.execute(REQUETE_AJOUT)
        rows = cur.fetchall()
        for row in rows:
            id_app = str(row)
            id_app = id_app.replace("(","")
            id_app = id_app.replace(",)","")

        cur.close()
        conn.close()
        
        return id_app

    except sqlite3.Error as error:
        print("Erreur : ", error)
    except UnboundLocalError as error:
        print("Erreur application inconnue : ", error)
        sys.exit()
    


def ajout_bdd_version_minmax(CVE, version_min, version_max):
    try:
        conn = sqlite3.connect('..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        REQUETE_AJOUT = """INSERT INTO CVE_VERSION (IDCVE, version_min, Version_max)
                        SELECT IDCVE, '"""+version_min+"""', '"""+version_max+"""'
                        FROM CVES
                        WHERE Titre_CVE = \'"""+CVE+"""\'"""

        cur.executescript(REQUETE_AJOUT)


        cur.close()
        conn.close()
    except sqlite3.Error as error:
        print("Erreur ajout_BDD_version:", error)





def ajout_BDD_version(CVE, version):
    try:
        conn = sqlite3.connect('..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
    
        REQUETE_AJOUT = """INSERT INTO CVE_VERSION (IDCVE, version)
                        SELECT IDCVE, '"""+version+"""'
                        FROM CVES
                        WHERE Titre_CVE = \'"""+CVE+"""\'"""

        cur.executescript(REQUETE_AJOUT)


        cur.close()
        conn.close()
    except sqlite3.Error as error:
        print("Erreur ajout_BDD_version:", error)



def ajout_bdd_CVE(Val_titre, Val_date, Val_criticite, Val_app, Val_description):
    try:
        conn = sqlite3.connect('..\ProjetCyber2\db\db.db')
        cur = conn.cursor()
        print(Val_titre, Val_date, Val_criticite, Val_app, Val_description)
        REQUETE_AJOUT = """UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='CVES'; 
        INSERT INTO CVES (Titre_CVE, Date_publication, Criticité, IDApplication, Description) 
        VALUES (\'"""+Val_titre+"""\', \'"""+Val_date+"""\', \'"""+Val_criticite+"""\', \'"""+Val_app+"""\', \'"""+Val_description+"""\');"""

        cur.executescript(REQUETE_AJOUT)

        cur.close()
        conn.close()
    except sqlite3.Error as error:
        print("Erreur ajout_bdd_CVE :", error)







def get_version(desc):

    liste_version = []

    versions_app = 0
    versions_app = re.findall('\s*([\d.]+\sto\s[\d.]+)', desc)
    versions = re.findall('\s([\d.]+)', desc)
    if versions_app == []:
        if versions !=None:
            for ver in versions:
                liste_version.append(ver)
    else:
        for val in versions_app:
            liste_version.append(val)
    
    return liste_version





def get_CVE_1(product_CVE, vendor_CVE, type_CVE):

    product_CVE_URL = product_CVE

    if len(product_CVE_URL.split())>1:
        first, last = product_CVE_URL.split()
        product_CVE_URL = first+'+'+last

    #----------------------------------ETAPE 1------------------------------------


    url = "https://www.cvedetails.com/product-search.php?vendor_id=0&search="+product_CVE_URL 

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find('table', attrs={'class': 'listtable'})
    results = table.find_all('tr')



    nb_ligne=0
    for result in results:
        data = result.find_all('td')
        nb_ligne=nb_ligne+1

    for result in results:
        data = result.find_all('td')
        if nb_ligne <= 2:
            if len(data) == 0:
                continue
            product = data[1].getText()
            product = str(product).strip()
            url_CVE = data[3].a['href']
            if product == product_CVE:
                return site+url_CVE
        else:
            if len(data) == 0:
                continue
            product = data[1].getText()
            product = str(product).strip()
            url_CVE = data[3].a['href']
            vendor = data[2].getText()
            vendor = str(vendor).strip()
            type = data[4].getText()
            type = str(type).strip()


            if product == product_CVE:
                if vendor == vendor_CVE:
                    if type == type_CVE:
                        # print(product, vendor, type)
                        return site+url_CVE


def get_CVE_3(url,id_app):

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find('table', attrs={'class': 'searchresults sortable'})
    results = table.find_all('tr')


    nb_cve = 0
    for result in results:
        data = result.find_all('td')
        if len(data) == 0:
            continue
        try:
            date_publication = data[5].getText()
            date_publication = str(date_publication).strip()
            if postdate(date_limite, date_publication) ==False:
                continue
            score = data[7].getText()
            score = float(score)
            if score < 4:
                continue
            if score >= 8:
                criticite = 'Critique'
            elif score <=5.99:
                criticite = 'Moyenne'
            else:
                criticite = 'Importante'
            CVE = data[1].getText()
            CVE = str(CVE).strip()
            desc = description_cve(CVE)  
            nb_cve = nb_cve + 1
            versions = get_version(desc)
            ajout_bdd_CVE(CVE, date_publication, criticite, id_app, desc)
            print(CVE, "ajouté à la bdd")
            for version in versions:
                if re.findall('\s*([\d.]+\sto\s[\d.]+)', version):
                    version_min,version_max = version.split('to')
                    print(CVE, version_min, version_max)
                    ajout_bdd_version_minmax(CVE, version_min,version_max)
                else:
                    ajout_BDD_version(CVE, version)
        except IndexError:
            CVE = 'null'

    

def get_CVE_via_mitre(app):
    url = "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword="+app

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find_all('div',  {'id': 'TableWithRules'})


    x = 0
    for result in table:
        tr = result.find_all('tr')
        for td in tr:
            data = td.find_all('td')
            if len(data) == 0:
                continue
            try:
                CVE = data[0].getText()
                CVE = str(CVE).strip()
                annee = CVE[4:8]
                annee = int(annee)
                if annee - annee_limite <0:
                    continue
                if cve_concern_product(CVE,app) == False:
                    continue
                description = data[1].getText()
                description = str(description).strip()
                ver = get_version(description)

                for a in ver:
                    print(a,CVE,app)
                x=x+1
            except IndexError:
                CVE = 'null'
    print(x)


        
def compare_version(version_app, version_vuln, version_vuln_min, version_vuln_max):
    if version_vuln != '0':
        return version.parse(version_app) < version.parse(version_vuln)
    elif version_vuln_min != '0' and version_vuln_max != '0':
        print(version_vuln_min,version_app,version_vuln_max)
        if (version.parse(version_app) >= version.parse(version_vuln_min)) == True and (version.parse(version_app) <= version.parse(version_vuln_max)) == True:
            return True
        else:
            return False







    





    