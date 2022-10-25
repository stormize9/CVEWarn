from flask.templating import render_template
from config.config import get_admin_password, get_admin_username
from flask import session,url_for,redirect
from functools import wraps

import werkzeug.serving
import OpenSSL


admin_username = get_admin_username()
admin_password = get_admin_password()

def requires_admin_authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session["admin"] :
            return render_template('forbidden.html')
            
        return f(*args, **kwargs)
    return decorated


def requires_user_authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('routes.login'))
        if kwargs['infra_id'] != str(session['id']):
            return render_template('forbidden.html')
        return f(*args, **kwargs)
    return decorated

class PeerCertWSGIRequestHandler( werkzeug.serving.WSGIRequestHandler ):
    """
    We subclass this class so that we can gain access to the connection
    property. self.connection is the underlying client socket. When a TLS
    connection is established, the underlying socket is an instance of
    SSLSocket, which in turn exposes the getpeercert() method.

    The output from that method is what we want to make available elsewhere
    in the application.
    """
    def make_environ(self):
        """
        The superclass method develops the environ hash that eventually
        forms part of the Flask request object.

        We allow the superclass method to run first, then we insert the
        peer certificate into the hash. That exposes it to us later in
        the request variable that Flask provides
        """
        environ = super(PeerCertWSGIRequestHandler, self).make_environ()
        x509_binary = self.connection.getpeercert(True)
        x509 = OpenSSL.crypto.load_certificate( OpenSSL.crypto.FILETYPE_ASN1, x509_binary )
        environ['peercert'] = x509
        return environ