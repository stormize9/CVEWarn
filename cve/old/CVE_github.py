from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import datetime
import json
import time
import re
import multiprocessing
from github import Github
from github.ContentFile import ContentFile

ACCESS_TOKEN = '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'

g = Github(ACCESS_TOKEN)


def get_score_CVE(CVE):
    url = 'https://www.cvedetails.com/cve-details.php?t=1&cve_id='+CVE



    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    soup = BeautifulSoup(webpage, 'html.parser')
    cvss = soup.find('div', attrs={'class': 'cvssbox'})
    score = cvss.getText()
    score = float(score)
    

    return score

def cve_concern_product(CVE,product): #Check si le produit est bien concerné par la CVE (via github)

    repo = CVE+"repo:CVEproject/cvelist"
    results = g.search_code(repo,'indexed','desc')
    for result in results:
            data = result.decoded_content.decode()
            data = json.loads(data)

            produit = data['affects']['vendor']['vendor_data'][0]['product']['product_data'][0]['product_name']
            if produit == []:
                return True
            if produit == product:
                return True
            else:
                return False


def get_CVE_github(app):
    repo = app+"repo:CVEproject/cvelist"
    results = g.search_code(repo,'indexed','desc')
    nb_CVE = 0
    for result in results:
            data = result.decoded_content.decode()
            data = json.loads(data)

            if nb_CVE == 50:
                break


            id = data['CVE_data_meta']['ID']
            score = get_score_CVE(id)

            if score < 6:
                continue

            produit = data['affects']['vendor']['vendor_data'][0]['product']['product_data'][0]['product_name']
            if produit == app:
                data = data['affects']['vendor']['vendor_data'][0]['product']['product_data'][0]['version']['version_data']


                for version in data:
                    version_concernee = version['version_value']
                    version = re.findall('\d.+', version_concernee)
                    print(version,' : ', id, produit, score)
                nb_CVE = nb_CVE+1




if __name__ == '__main__':

    product = 'Node.js'
    v = '94.0.4006.81'

    p = multiprocessing.Process(target=get_CVE_github, args=(product,))

    p.start()
    p.join(600)

    if p.is_alive():
        print ("Timeout expire")
        p.terminate()
        p.join()



