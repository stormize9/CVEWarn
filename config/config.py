import configparser
from optparse import Values
import random
import string

config_path = "./config/settings.ini"

def config_dict():
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

config = config_dict()

def random_string(string_length=10):
    letters = string.ascii_lowercase + '0123456789'
    return ''.join(random.choice(letters) for i in range(string_length))

def change_secret_key():
    config.set('global', 'secret', random_string(20))
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    return

def get_debug():
    if config.get('global', 'debug') == "1":
        return True
    else : 
        return False

def get_host():
    return config.get('network', 'host')

def get_port():
    return config.get('network', 'port')

def get_secret_key():
    return config.get('global', 'secret')   

def get_admin_username():
    return config.get('admin','username')

def get_admin_password():
    return config.get('admin','password')

def ssl_enabled():
    if config.get('ssl','ssl') == "1":
        return True
    return False

def cert_access_enabled():
    if config.get('ssl','cert_access') == "1":
        return True
    return False

def get_cert_path_ca():
    return config.get('ssl','cert_ca')

def get_priv_key_path_ca():
    return config.get('ssl','priv_key_ca')

def get_cert_path_srv():
    return config.get('ssl','cert_srv')

def get_priv_key_path_srv():
    return config.get('ssl','priv_key_srv')

def set_cert_path_srv():
    config.set('ssl', 'cert_srv', './config/server.key')
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
def set_priv_key_path_srv():
    config.set('ssl', 'priv_key_srv', './config/server.key')
    with open(config_path, 'w') as configfile:
        config.write(configfile)

def set_cert_path_ca():
    config.set('ssl', 'cert_ca', './config/ca.key')
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
def set_priv_key_path_ca():
    config.set('ssl', 'priv_key_ca', './config/ca.key')
    with open(config_path, 'w') as configfile:
        config.write(configfile)
