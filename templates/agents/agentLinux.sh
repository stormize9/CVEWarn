#!/bin/bash

SRV_PROTOCOLE="http"
SRV_IP="172.16.3.20"
SRV_PORT=80

cmd_exist () {
    type $1 > /dev/null 2>&1
    return $?
}

#Récupération IP et MAC par Interface et logiciels installé
interface=""
if cmd_exist ip ; then
    interface=$(ip route | grep default | cut -d' ' -f 5 | head -n 1)
    IP=$(ip add show $interface  | grep "inet " | tr -s ' ' | cut -d' ' -f 3 | sed 's#/.*##' | head -n 1)
    MAC=$(ip add show $interface  | grep "link/ether" | tr -s ' ' | cut -d' ' -f 3 | head -n 1)
else
    if cmd_exist route ; then
        interface=$(route | grep default | tr -s ' ' | cut -d' ' -f8 | head -n 1)
    elif cmd_exist netstat ; then
        interface=$(netstat -rn | grep ^0.0.0.0 | tr -s ' ' | cut -d' ' -f 8 | head -n 1)
    fi
    if cmd_exist ifconfig ; then
        IP=$(ifconfig $interface | grep "inet " | tr -s ' '| cut -d' ' -f 3)
        MAC=$(ifconfig $interface | grep "ether" | tr -s ' '| cut -d' ' -f 3)
    fi
fi


NOMOS=$(grep "^NAME=" /etc/os-release | cut -d '"' -f 2)
VERSION=$(grep "^VERSION_ID=" /etc/os-release | cut -d '"' -f 2)
HOSTNAME=$(hostname)
IDENTIFIER=$(echo "$HOSTNAME.$MAC" | md5sum | cut -d" " -f 1)
ID_INFRA={{infra_id}}
myjson="""
{
  \"id_infrastructure\" : \"$ID_INFRA\",
  \"IDENTIFIER\" : \"$IDENTIFIER\",
  \"IP\" : \"$IP\",
  \"Hostname\" : \"$HOSTNAME\",
  \"OS\" : {
    \"Nom_OS\" : \"$NOMOS\",
    \"VersionOS\" : \"$VERSION\"
  },
  \"Application\" :
        [
            {
            \"Nom_Application\" : \"\",
            \"Version_Application\" : \"\"
            }
"""

old_IFS=$IFS  # sauvegarde du séparateur de champ  
IFS=$'\n'     # nouveau séparateur de champ, le caractère fin de ligne  
prevNameApp=" "
for ligne in $(dpkg -l --no-pager | tail -n+6 | tr -s ' ' |grep -v "lib")
do  
    nameAPP=$(echo $ligne | cut -d ' ' -f 2)
    versionAPP=$(echo $ligne | cut -d ' ' -f 3)

    # Permet de ne prendre que le maitre d'une catégorie (exemple: python3 et python3-tools)
    if ! [[ $(echo $nameAPP | grep $prevNameApp) ]]; then
        prevNameApp="^$nameAPP*"
        myjson=$myjson""",{
            \"Nom_Application\" : \"$nameAPP\",
            \"Version_Application\" : \"$versionAPP\"
        }
        """
    fi
done  
IFS=$old_IFS  # rétablissement du séparateur de champ par défaut

myjson=$myjson"]}"

echo $myjson

curl -i \
-H "Content-Type:application/json; charset=utf-8" \
-X POST --data "$myjson" $SRV_PROTOCOLE"://"$SRV_IP":"$SRV_PORT"/api/v1/update"
