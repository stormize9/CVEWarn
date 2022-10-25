import random
from ssl import ALERT_DESCRIPTION_HANDSHAKE_FAILURE
from OpenSSL import crypto
from config.config import get_priv_key_path_ca, get_cert_path_ca, get_priv_key_path_srv, get_cert_path_srv, set_cert_path_srv, set_priv_key_path_srv, set_cert_path_ca, set_priv_key_path_ca 
import bcrypt

def load_crypto_cert(cert_file_path):
    with open(cert_file_path, "r") as f:
        cert_buf = f.read()

    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_buf)
    return cert

def load_crypto_PK(pk_file_path):
    with open(pk_file_path, "r") as f:
        cert_buf = f.read()
    cert = crypto.load_privatekey(crypto.FILETYPE_PEM, cert_buf)
    return cert


def generate_ca():
    ca_key = crypto.PKey()
    ca_key.generate_key(crypto.TYPE_RSA, 2048)

    ca_cert = crypto.X509()
    ca_cert.set_version(2)
    ca_cert.set_serial_number(random.randint(50000000,100000000))

    ca_subj = ca_cert.get_subject()
    ca_subj.commonName = "CVE Warn CA"

    ca_cert.add_extensions([
        crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=ca_cert),
    ])

    ca_cert.add_extensions([
        crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always", issuer=ca_cert),
    ])

    ca_cert.add_extensions([
        crypto.X509Extension(b"basicConstraints", False, b"CA:TRUE"),
        crypto.X509Extension(b"keyUsage", False, b"keyCertSign, cRLSign"),
    ])

    ca_cert.set_issuer(ca_subj)
    ca_cert.set_pubkey(ca_key)
    ca_cert.sign(ca_key, 'sha256')

    ca_cert.gmtime_adj_notBefore(0)
    ca_cert.gmtime_adj_notAfter(10*365*24*60*60)

    # Save certificate
    with open("config/ca.crt", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, ca_cert))

    # Save private key
    with open("config/ca.key", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key))

def generate_client_cert(cn,name,server=False):

    client_key = crypto.PKey()
    client_key.generate_key(crypto.TYPE_RSA, 2048)

    client_cert = crypto.X509()
    client_cert.set_version(2)
    client_cert.set_serial_number(random.randint(50000000,100000000))

    client_subj = client_cert.get_subject()
    client_subj.commonName = "Client"

    client_cert.add_extensions([
        crypto.X509Extension(b"basicConstraints", False, b"CA:FALSE"),
        crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash", subject=client_cert),
    ])
    
    ca_cert = load_crypto_cert(get_cert_path_ca())

    client_cert.add_extensions([
        crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always", issuer=ca_cert),
        crypto.X509Extension(b"extendedKeyUsage", False, b"clientAuth"),
        crypto.X509Extension(b"keyUsage", False, b"digitalSignature"),
    ])

    ca_subj = ca_cert.get_subject()
    ca_subj.commonName = cn

    ca_key = load_crypto_PK(get_priv_key_path_ca())

    client_cert.set_issuer(ca_subj)
    client_cert.set_pubkey(client_key)
    client_cert.sign(ca_key, 'sha256')

    client_cert.gmtime_adj_notBefore(0)
    client_cert.gmtime_adj_notAfter(10*365*24*60*60)
    if server:
        # Save certificate
        with open("config/"+name+".crt", "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert))

        # Save private key
        with open("config/"+name+".key", "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key))
    else :
        # Save certificate
        with open("cert_client/"+name+".crt", "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, client_cert))

        # Save private key
        with open("cert_client/"+name+".key", "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key))

def init_server_cert():
    if get_priv_key_path_srv() == "" or get_cert_path_srv() == "":
        generate_client_cert("cvewarn.local","server",True)
        set_cert_path_srv()
        set_priv_key_path_srv()

def init_CA_cert():
    if get_priv_key_path_ca() == "" or get_cert_path_ca() == "":
        generate_ca()
        set_cert_path_ca()
        set_priv_key_path_ca()

def init():
    init_CA_cert()
    init_server_cert()


def hash(string):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bytes(string,'UTF-8'), salt)
    return hashed

def check_pass(password,hash):
    password=password.encode('UTF-8')
    if type(hash) != bytes: 
        hash=hash.encode('UTF-8')
    return bcrypt.checkpw(password, hash)