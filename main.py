# -*- coding: utf-8 -*-

from flask import Flask,render_template
from flask_caching import Cache

from config.config import get_secret_key,get_debug,get_host, get_port, change_secret_key, ssl_enabled, get_priv_key_path_ca, get_cert_path_ca, cert_access_enabled
from db.db import Database
from module import authentification, crypto

from routes import myroutes

global mydb
mydb = Database()

app = Flask(__name__)

app.register_blueprint(myroutes)

app.config['SECRET_KEY'] = get_secret_key()


cache = Cache(config={'CACHE_TYPE': 'simple', "CACHE_DEFAULT_TIMEOUT": 300})
cache.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    
    if cert_access_enabled():
        import ssl
        crypto.init()

        app_key = get_priv_key_path_ca()
        app_cert = get_cert_path_ca()
        ca_cert = get_cert_path_ca()

        ssl_context = ssl.create_default_context( purpose=ssl.Purpose.CLIENT_AUTH,
                                          cafile=ca_cert )
        ssl_context.load_cert_chain( certfile=app_cert, keyfile=app_key, password=None )
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        app.run(
            ssl_context=ssl_context, 
            request_handler=authentification.PeerCertWSGIRequestHandler,
            host=get_host(),
            port=get_port(),
            debug=get_debug(),
            threaded=True)

    elif ssl_enabled():
        import ssl
        crypto.init()
        
        app_key = get_priv_key_path_ca()
        app_cert = get_cert_path_ca()

        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(app_cert, app_key)
        app.run(
            ssl_context=context,
            host=get_host(),
            port=get_port(),
            debug=get_debug(),
            threaded=True)

    else:
        app.run(
            host=get_host(),
            port=get_port(),
            debug=get_debug(),
            threaded=True)
    
