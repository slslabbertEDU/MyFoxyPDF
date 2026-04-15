import pytest
import os
import sys
import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from security.signatures import create_self_signed_cert, sign_pdf, validate_pdf

def test_sign_pdf(tmp_path):
    cert_path = tmp_path / "cert.pem"
    key_path = tmp_path / "key.pem"
    create_self_signed_cert(str(cert_path), str(key_path))

    in_pdf = tmp_path / "in.pdf"
    out_pdf = tmp_path / "out.pdf"

    doc = fitz.open()
    doc.new_page()
    doc.save(str(in_pdf))
    doc.close()

    sign_pdf(str(in_pdf), str(out_pdf), str(cert_path), str(key_path))

    assert out_pdf.exists()

    doc2 = fitz.open(str(out_pdf))
    widgets = list(doc2[0].widgets())
    assert len(widgets) > 0
    assert widgets[0].field_type == fitz.PDF_WIDGET_TYPE_SIGNATURE
    doc2.close()
    assert "Signature" in validate_pdf(str(out_pdf))
