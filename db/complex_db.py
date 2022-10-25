from main import mydb

##########################
##    HOST              ##
##########################

def ajout_host_if_not(id_infrastructure,Identifier,ip,hostname,osname,osversion):
    result = mydb.select_host(Identifier)
    if len(result) == 0 : 
        mydb.insert_host(Identifier,ip,hostname,ajout_os_if_not(osname,osversion),id_infrastructure)
        result = mydb.select_host(Identifier)
    return result[0]["id_host"]

def ajout_host_by_OSREF(id_infrastructure,Identifier,ip,hostname,osref):
    mydb.insert_host(Identifier,ip,hostname,osref,id_infrastructure)
    result = mydb.select_host(Identifier)
    return result[0]["id_host"]

def everything_from_idhost(idhost):
    host = mydb.select_host(idhost)
    os = mydb.select_os_information_from_id_os()


    return host

##########################
##    OS                ##
##########################

def ajout_os_if_not(nomOS,versionOS):
    result = mydb.select_id_os_from_OS(nomOS,versionOS)
    if len(result) == 0 : 
        mydb.insert_os(nomOS,versionOS)
        result = mydb.select_id_os_from_OS(nomOS,versionOS)
    return result[0]["id_os"]


##########################
##    APP               ##
##########################

def ajout_app_if_not(nomApp,versionApp):
    result = mydb.select_id_app(nomApp,versionApp)
    if len(result) == 0 : 
        mydb.insert_app(nomApp,versionApp)
        result = mydb.select_id_app(nomApp,versionApp)
    return result[0]["id_application"]

