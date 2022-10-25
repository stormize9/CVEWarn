from CVE_details import *
import github



product = 'Wireshark'
vendor = 'Wireshark'
type = 'Application'



if __name__ == "__main__":
    try:
        id_app = get_idApp_by_name(product)
        url = get_CVE_1(product, vendor, type)
        # url2 = get_CVE_2(url)
        INFO_CVE = get_CVE_3(url,id_app)
    except ValueError:
            print("Erreur problème sur la récupération des CVE de l'application",product)
