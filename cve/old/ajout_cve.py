import github
from CVE_details import *
from CVE_mitre import *
from CVE_details import *
from CVE_details import get_url_details, get_CVE_details





product = 'Blender'
vendor = ''
type = 'Application'
version = '2.78'


liste_finale = []

# liste_url_version = get_url_details(product, vendor, type, version)


# if liste_url_version == False:
#     print("Aucune info via CVE_details")
# else:
#     for url in liste_url_version:
#         liste_cve = get_CVE_details(url)
#         for cve,val in liste_cve.items():
#             print(cve,val[0])
            
    
liste_cve_mitre = get_CVE_by_MITRE(product,version)

if liste_cve_mitre == False:
    print("Aucune info via MITRE")
else:
    for cve in liste_cve_mitre:
        liste_finale.append(cve)



# for cve in liste_finale:
#     print(cve)

