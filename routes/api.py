from routes import myroutes

from flask import request
from db.complex_db import *

@myroutes.route("/api/v1/newos", methods=['POST'])
def newOS():
    json_update = request.get_json(force=True)
    ajout_os_if_not(json_update["NomOS"],json_update["VersionOS"])
    return "OK"

@myroutes.route("/api/v1/newhote", methods=['POST'])
def newhote():
    json_update = request.get_json(force=True)
    ajout_host_by_OSREF(json_update["id_infrastructure"],json_update["IDENTIFIER"],json_update["IP"],json_update["Hostname"],json_update["OS_ref"])
    return "OK"

@myroutes.route('/api/v1/update', methods=['POST'])
def update_from_agent():
    json_update = request.get_json(force=True)
    id_infrastructure=json_update["id_infrastructure"]
    identifier=json_update["IDENTIFIER"]
    ip=json_update["IP"]
    hostname=json_update["Hostname"]
    osname=json_update["OS"]["Nom_OS"]
    osversion=json_update["OS"]["VersionOS"]
    idhost = ajout_host_if_not(id_infrastructure,identifier,ip,hostname,osname,osversion)
    mydb.delete_all_associate_apps_host(idhost)
    if "Application" in json_update: 
        for element in json_update["Application"]:
            idapp = ajout_app_if_not(element["Nom_Application"],element["Version_Application"])
            mydb.insert_associate_host_apps(idapp,idhost)
    return "OK"