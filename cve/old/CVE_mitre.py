from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from compare_version import *
from regex import *
import datetime
import sqlite3
import sys
import re
from packaging import version
from flask import scaffold




print(sys.path)



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


site = "https://cve.mitre.org/cgi-bin/cvekey.cgi?"



def get_description_cve(CVE):
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




def get_CVE_by_MITRE(product,version):

    liste_CVE = []

    url = site+"keyword="+product

    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')

    table = soup.find_all('div',  {'id': 'TableWithRules'})

    x=0
    nb_ver_false = 0
    for result in table:
        tr = result.find_all('tr')
        for td in tr:
            data = td.find_all('td')
            if len(data) == 0:
                continue
            x=x+1
            if x == 500:
                break
            try:
                description = data[1].getText()
                CVE = data[0].getText()
                CVE = str(CVE).strip()
                liste_app_CVE = get_app_by_CVE(CVE)
                if liste_app_CVE == False:
                    continue
                if product not in liste_app_CVE:
                    if product.capitalize() not in liste_app_CVE:
                        continue
                liste_version = get_version(description)
                if liste_version == False:
                    continue
                for ver in liste_version:
                    if split_version(ver,version):
                        liste_CVE.append(CVE)
                    else:
                        nb_ver_false = nb_ver_false + 1

            except IndexError:
                CVE = 'null'


    return liste_CVE



