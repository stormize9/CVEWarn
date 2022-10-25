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

def ajout_bdd(id,date,summary):
    try:
        mydb.insert_last_cve(id,date,summary)
    except sqlite3.IntegrityError as error:
        print("CVE déjà existante")


def get_id_by_CVE(id):
    rows = mydb.select_id_cve(id)
    for line in rows:
        return line['id_cve']


def requete(nb):
    nb = str(nb)
    url = "https://cvepremium.circl.lu/api/last?limit="+nb

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        result = json.loads(response.text)


            
        for cve in result:
            id = cve['id']
            date = cve['Published']
            date = traduction_date(date)
            summary = cve['summary']
            summary = summary.replace("'","")
            versions = cve['vulnerable_product']
            ajout_bdd(id,date,summary)



