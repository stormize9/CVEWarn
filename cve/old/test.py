dico = {}
dico['CVE1'] = ['a1','b1','c1']
dico['CVE2'] = ['a2','b2','c2']
print(dico)
for key,val in dico.items():
    print(val[2])