from urllib.request import Request, urlopen
import json 
import requests
import re
import sqlite3
import sys
from bs4 import BeautifulSoup

con = sqlite3.connect('../db/db.db')
cur = con.cursor()


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


def requete(vendor_url,product_url,version_product):
    version_product = re.search('(\d+\.){1,}(\d+)', version_product)
    version_product = version_product.group()

    if len(vendor_url.split()) > 1:
        vendor_url1,vendor_url2 = vendor_url.split()
        vendor_url1 = vendor_url1.lower()
        vendor_url2 = vendor_url2.lower()
        vendor_url = vendor_url1+"_"+vendor_url2
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
                            print(id,product,ver)
                    else:
                        continue

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


product_url = "blender kjzbs"
version_product = "2.36"

product_url = product_url.lower()


get_vendor(product_url,version_product)


