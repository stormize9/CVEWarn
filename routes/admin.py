from routes import myroutes
from module import authentification,crypto
from flask import redirect, render_template, request, url_for
from main import mydb
from cve import CVE

#######################################
### Admin Page                      ###
#######################################


@myroutes.route("/admin")
@authentification.requires_admin_authorization
def admin():
    return render_template("admin/admin.html")

@myroutes.route("/admin/clients")
@authentification.requires_admin_authorization
def admin_clients():
    data = {"users" : mydb.select_all_users()}
    return render_template("admin/clients.html", data=data)


@myroutes.route("/admin/clients/adduser", methods=['POST'])
@authentification.requires_admin_authorization
def admin_adduser():
    mydb.insert_user(request.form['nom'],request.form['prenom'],\
        request.form['email'],request.form['tel'],request.form['login'],\
        crypto.hash(request.form['password']),request.form['name_company']
    )
    return redirect(url_for("routes.admin_clients"))

@myroutes.route('/admin/update_CVE/')
@authentification.requires_admin_authorization
def update_CVE():
        CVE.main()
        return redirect('/admin')