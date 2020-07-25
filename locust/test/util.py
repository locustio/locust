import os
import socket

from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from contextlib import contextmanager
from tempfile import NamedTemporaryFile


@contextmanager
def temporary_file(content, suffix="_locustfile.py"):
    f = NamedTemporaryFile(suffix=suffix, delete=False)
    f.write(content.encode("utf-8"))
    f.close()
    try:
        yield f.name
    finally:
        if os.path.exists(f.name):
            os.remove(f.name)


def get_free_tcp_port():
    """
    Find an unused TCP port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def create_tls_cert(hostname):
    """ Generate a TLS cert and private key to serve over https """
    key = rsa.generate_private_key(public_exponent=2 ** 16 + 1, key_size=2048, backend=default_backend())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])
    now = datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1000)
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=10 * 365))
        .sign(key, hashes.SHA256(), default_backend())
    )
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return cert_pem, key_pem
