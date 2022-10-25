
from routes import myroutes
from module import authentification, crypto
from flask import render_template, redirect, session, url_for, request,flash
from flask.helpers import send_from_directory
from main import mydb, cache

@cache.cached()
@myroutes.route('/favicon.ico')
def favicon():
    return send_from_directory('static','logo/favicon.ico', mimetype='image/vnd.microsoft.icon')

@myroutes.route("/")
def racine():
    if 'id' not in session:
        return redirect(url_for('routes.login'))
    else:
        if session['admin'] == True:
            return redirect(url_for('routes.admin'))
        else:
            return redirect(url_for('routes.index',infra_id=str(session['id'])))

@myroutes.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        
        if request.form['username'] == authentification.admin_username and crypto.check_pass(request.form['password'],authentification.admin_password):
            session['admin'] = True
            return redirect(url_for('routes.admin'))
        db_return = mydb.select_id_infrastructure_from_login(request.form['username'])
        if len(db_return) > 0 and crypto.check_pass(request.form['password'],db_return[0]["password"]):
            session["id"] = db_return[0]["id_infrastructure"]
            session['admin'] = False
            return redirect(url_for('routes.index',infra_id=session['id']))
        flash("Erreur de connexion","danger")
        return render_template("login.html")
        
@myroutes.route("/logout")
def logout():
    try:
        del session['id']
    except:
        pass
    return redirect(url_for('routes.login'))

