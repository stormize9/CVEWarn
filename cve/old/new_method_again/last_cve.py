import requests
import json 
import re
import sqlite3
import sys


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
        cpe_modif
        return cpe_modif[2]



version = get_version_via_cpe( "cpe:2.3:a:mariadb:mariadb:10.2.5:*:*:*:*:*:*:*")
print(version)


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


# url = "https://cvepremium.circl.lu/api/last?limit=5"
# payload={}
# headers = {}

# response = requests.request("GET", url, headers=headers, data=payload)

# result = json.loads(response.text)

# for cve in result:
#     liste_ver = []
#     id = cve['id']
#     date = cve['Modified']
#     date = traduction_date(date)

#     summary = cve['summary']
#     summary = summary.replace("'","")
#     versions = cve['vulnerable_product']
#     for version in versions:
#         ver = get_version_via_cpe(version)
#         if ver != None:
#             if ver not in liste_ver:
#                 print(ver)
#                 liste_ver.append(ver)
