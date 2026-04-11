from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

def create_self_signed_cert(cert_path, key_path):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.x509 import NameOID
    from cryptography import x509
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"MyFoxyPDF Test"),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10)
    ).sign(key, hashes.SHA256())

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

def sign_pdf(input_pdf, output_pdf, cert_pem, key_pem):
    signer = signers.SimpleSigner.load(key_pem, cert_pem)

    with open(input_pdf, 'rb') as doc_file:
        w = IncrementalPdfFileWriter(doc_file)
        with open(output_pdf, 'wb') as out_file:
            signers.sign_pdf(
                w, signers.PdfSignatureMetadata(field_name='Signature1'),
                signer=signer,
            )
            w.write(out_file)
