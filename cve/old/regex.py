import re


# def test():
#     x=5
#     if x==3:
#         print(3)
#     if x==2:
#         print(2)
#     elif x == 5:
#         print(5)
#     elif x == 5:
#         print('a')

# test()

def exceptions(liste_version,version,desc):
    for ver in version:
        ver = ver.strip()
        if ver == '.' or ver == '+' or ver.startswith('802') or ver =='3d':
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
  
print(get_version("The dissect_packet function in epan/packet.c in Wireshark 1.4.x before 1.4.11 and 1.6.x before 1.6.5 allows remote attackers to cause a denial of service (application crash) via a long packet in a capture file, as demonstrated by an airopeek file."))
