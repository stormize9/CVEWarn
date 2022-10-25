from flask import flash, redirect, render_template, url_for, request, send_from_directory
from module import authentification
from routes import myroutes
from main import mydb
from cve import last_cve
from cve import CVE
import os
import re
import urllib3
import requests


@myroutes.route("/ui/<infra_id>/")
@authentification.requires_user_authorization
def index(infra_id,page=1):
    url = "https://cvepremium.circl.lu/api/dbinfo"
    response = requests.request("GET", url, verify=False)
    json_data = response.json()
    size_cve = json_data['cves']['size']
    
    last_cve_data = {"cve" : mydb.select_last_cve()}
    nb_cve = mydb.select_nb_cve()

    nb_last_cve = mydb.nb_last_CVE()
    return render_template("dashboard.html",infra_id=infra_id,nb_last_cve=nb_last_cve,nb_cve=nb_cve,last_cve_data=last_cve_data,size_cve=size_cve)


@myroutes.route("/ui/<infra_id>/host/")
@authentification.requires_user_authorization
def list_host(infra_id):
    hotes = mydb.select_all_host_information_os(infra_id)
    oss = mydb.select_all_os()
    apps = mydb.select_all_apps_from_infra(infra_id)
    return render_template("list_host.html", hotes=hotes,infra_id=infra_id,oss=oss,apps=apps)

@myroutes.route("/ui/<infra_id>/cve")
@authentification.requires_user_authorization
def cve(infra_id):
    data = {"cve" : mydb.select_all_cve(infra_id)}
    nb_cve = mydb.select_all_cve(infra_id)
    app_imp = mydb.app_impacte(infra_id)
    highest_cve = mydb.highest_cve(infra_id)
    host_impacte = mydb.host_impacte(infra_id)
    if not app_imp:
        return render_template("cve.html",infra_id=infra_id,data=data,nb_cve=nb_cve)
    else:
        return render_template("cve.html", data=data,nb_cve=nb_cve,app_imp=app_imp[0],infra_id=infra_id,highest_cve=highest_cve,host_impacte=host_impacte)

@myroutes.route('/ui/<infra_id>/host/<host_id>/')
@authentification.requires_user_authorization
def detail_host(infra_id,host_id):
    host_information_with_apps = mydb.select_host_information_with_app(host_id)
    return render_template("host_advanced.html", data_host_and_apps=host_information_with_apps,infra_id=infra_id)

@myroutes.route("/ui/<infra_id>/settings", methods=['GET'])
@authentification.requires_user_authorization
def settings(infra_id):
    user = mydb.select_user(infra_id)[0]
    return render_template("settings.html",infra_id=infra_id,user=user)

@myroutes.route("/ui/<infra_id>/settings", methods=['POST'])
@authentification.requires_user_authorization
def settings_update(infra_id):
    mydb.update_user(request.form['update-profile-name'], \
        request.form['update-profile-prenom'], \
        request.form['update-profile-tel'], \
        request.form['update-profile-email'], \
        infra_id
        )
    return redirect(url_for('routes.settings',infra_id=infra_id))


@myroutes.route("/ui/<infra_id>/settings/agentlinux")
@authentification.requires_user_authorization
def agent_linux(infra_id):
    headers={ 'Content-Type':'application/octet-stream', 'Content-Disposition': 'attachment; filename="agentLinux.sh"'}
    return render_template("agents/agentLinux.sh",infra_id=infra_id),headers
    
@myroutes.route("/ui/<infra_id>/settings/agentwindows")
@authentification.requires_user_authorization
def agent_windows(infra_id):
    headers={ 'Content-Type':'application/octet-stream', 'Content-Disposition': 'attachment; filename="agentWindows.ps1"'}
    return render_template("agents/agentWindows.ps1",infra_id=infra_id),headers

@myroutes.route('/ui/<infra_id>/cve/approuv_<id_vuln>/')
@authentification.requires_user_authorization
def put_off_CVE(infra_id,id_vuln):
    mydb.put_off_CVE(id_vuln)
    return redirect('/ui/'+infra_id+'/cve')

@myroutes.route('/ui/<infra_id>/cve/<cve_id>/')
@authentification.requires_user_authorization
def detail_cve(infra_id,cve_id):
    data = {"cve" :  mydb.details_cve(cve_id)}
    return render_template("cve_advanced.html", data=data,infra_id=infra_id)



@myroutes.route('/ui/<infra_id>/cve/update_last_CVE/', methods=["GET"])
def update_last_CVE(infra_id):
        last_cve.requete(50)
        return redirect('/ui/'+infra_id)


