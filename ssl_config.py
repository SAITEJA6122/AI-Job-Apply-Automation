"""
SSL/TLS Configuration for HTTPS support.

This module provides utilities for generating self-signed SSL certificates
and configuring Flask to use HTTPS.
"""
import os
from pathlib import Path
from datetime import datetime, timedelta


def generate_self_signed_cert(cert_path: str, key_path: str):
    """
    Generate a self-signed SSL certificate.

    Args:
        cert_path: Path where certificate will be saved
        key_path: Path where private key will be saved

    Note:
        This is for development only. For production, use proper SSL certificates
        from a certificate authority like Let's Encrypt.
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
    except ImportError:
        raise ImportError(
            "cryptography library is required. Install with: pip install cryptography"
        )

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Write private key to file
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Naukri Automation"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("*.localhost"),
            x509.IPAddress("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write certificate to file
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Self-signed certificate generated: {cert_path}")
    print(f"Private key generated: {key_path}")
    print("Note: This is for development only. Use proper SSL certificates for production.")


def setup_ssl_context(cert_path: str, key_path: str):
    """
    Create SSL context for Flask.

    Args:
        cert_path: Path to SSL certificate
        key_path: Path to SSL private key

    Returns:
        SSL context dictionary
    """
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        raise FileNotFoundError(
            f"SSL certificate or key not found. "
            f"Certificate: {cert_path}, Key: {key_path}"
        )

    return {
        'ssl_context': (cert_path, key_path),
        'host': '0.0.0.0',
        'port': 5000
    }


def ensure_ssl_certs(cert_dir: str = 'ssl_certs'):
    """
    Ensure SSL certificates exist, generate if they don't.

    Args:
        cert_dir: Directory to store SSL certificates

    Returns:
        Tuple of (cert_path, key_path)
    """
    cert_dir_path = Path(cert_dir)
    cert_dir_path.mkdir(exist_ok=True)

    cert_path = cert_dir_path / 'cert.pem'
    key_path = cert_dir_path / 'key.pem'

    if not cert_path.exists() or not key_path.exists():
        print("Generating self-signed SSL certificates...")
        generate_self_signed_cert(str(cert_path), str(key_path))

    return str(cert_path), str(key_path)


if __name__ == '__main__':
    # Generate certificates for development
    cert, key = ensure_ssl_certs()
    print(f"\nCertificates ready:")
    print(f"Certificate: {cert}")
    print(f"Key: {key}")
