from packaging import version
import re

def compare_version(version_app, version_vuln, version_vuln_min, version_vuln_max):
    if version_vuln != '0':
        return version.parse(version_app) == version.parse(version_vuln)
    elif version_vuln_min != '0' and version_vuln_max != '0':
        if (version.parse(version_app) >= version.parse(version_vuln_min)) == True and (version.parse(version_app) <= version.parse(version_vuln_max)) == True:
            return True
        else:
            return False

def split_version(str_ver,version_app):
    if re.findall('\s*([\d.]+\sto\s[\d.]+)', str_ver):
        versionmin,x,versionmax = str_ver.split()
        version_vuln = '0'
        return compare_version(version_app, version_vuln, versionmin, versionmax)

    elif re.findall('\s*([\d.]+\sthrough\s[\d.]+)', str_ver):
        versionmax,x,versionmin = str_ver.split()
        version_vuln = '0'
        return compare_version(version_app, version_vuln, versionmin, versionmax)

    elif re.findall('(before\s[\d.]+)', str_ver):
        x,version_vuln = str_ver.split()
        return version.parse(version_app) <= version.parse(version_vuln)

    elif re.findall('(after\s[\d.]+)', str_ver):
        x,version_vuln = str_ver.split()
        return version.parse(version_app) >= version.parse(version_vuln)

    elif re.findall('([\d.]+)', str_ver):
        version_vuln = str_ver
        return version.parse(version_app) == version.parse(version_vuln)

            



# string = 'after 1.9.14-1'
# ver = '1.9.14-2'
# print(split_version(string,ver))