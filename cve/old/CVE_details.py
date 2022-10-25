from bs4 import BeautifulSoup, NavigableString, Tag
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import datetime
import sqlite3
import sys
import re
from packaging import version
from flask import scaffold

from CVE_mitre import *



site = 'https://www.cvedetails.com/'

liste_url_a_parcourir = []

def get_app_by_CVE(CVE):
    url = site+"cve-details.php?t=1&cve_id="+CVE
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')
    try:
        table = soup.find('table', attrs={'class': 'listtable'})
        results = table.find_all('tr')

        liste_app = []

        for result in results:
            data = result.find_all('td')
            if len(data) == 0:
                continue
            product = data[3].getText()
            product = str(product).strip()
            liste_app.append(product)

        return liste_app
    except AttributeError:
        return False
        


def get_url_details(product, vendor, type, version):
    url = "https://www.cvedetails.com/version-search.php?vendor="+vendor+"&product="+product+"&version="+version+"%"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find('table', attrs={'class': 'searchresults'})
    results = table.find_all('tr')

    try:
        for result in results:
            data = result.find_all('td')
            if len(data) == 0:
                continue
            product = data[1].getText()
            product = str(product).strip()
            nb = data[7].getText()
            nb = int(nb)
            if nb == 0:
                continue
            url_vuln_version = data[8]

            for url_vuln in url_vuln_version:
                # if len(url_vuln) == 0:
                #     continue
                if isinstance(url_vuln, NavigableString):
                    continue
                if isinstance(url_vuln, Tag):
                    val = url_vuln.getText()
                # data = url_vuln.find_all('a')
                if  val == "Vulnerabilities":
                    url_version = site+url_vuln.get('href')
                    liste_url_a_parcourir.append(url_version)
        
        return liste_url_a_parcourir
    except IndexError:
        return False


def get_CVE_details(url):

    liste_cve = {}

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
            # desc = get_description_cve(CVE)
            nb_cve = nb_cve + 1

            liste_cve[CVE] = [date_publication,criticite]

        except IndexError:
            CVE = 'null'

    return liste_cve





                

            


        





