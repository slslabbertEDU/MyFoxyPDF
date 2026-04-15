from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers


def create_self_signed_cert(cert_path, key_path):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509 import NameOID
    import datetime

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "MyFoxyPDF Test"),
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

    with open(cert_path, "wb") as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
    with open(key_path, "wb") as key_file:
        key_file.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )


def sign_pdf(input_pdf, output_pdf, cert_pem, key_pem):
    signer = signers.SimpleSigner.load(key_pem, cert_pem)

    with open(input_pdf, "rb") as doc_file:
        writer = IncrementalPdfFileWriter(doc_file)
        signed_bytes = signers.sign_pdf(
            writer,
            signers.PdfSignatureMetadata(field_name="Signature1"),
            signer=signer,
        )

    with open(output_pdf, "wb") as out_file:
        out_file.write(signed_bytes.getbuffer())


def validate_pdf(pdf_path):
    try:
        import fitz

        doc = fitz.open(pdf_path)
        for page in doc:
            for widget in page.widgets() or []:
                if widget.field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE:
                    doc.close()
                    return "Signature field detected in document."
        doc.close()
        return "No signature field found in document."
    except Exception as exc:
        return f"Validation failed: {exc}"
