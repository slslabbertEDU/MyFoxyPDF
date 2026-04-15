import os
import sys

import fitz

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from security.signatures import (
    create_self_signed_cert,
    export_validation_report,
    sign_pdf,
    validate_pdf,
)


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

    validation = validate_pdf(str(out_pdf))
    assert validation["valid"] is True
    assert validation["signatures"]
    assert "Detected" in validation["message"]


def test_export_validation_report(tmp_path):
    pdf_path = tmp_path / "input.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()

    result = validate_pdf(str(pdf_path))
    report_path = tmp_path / "report.txt"
    export_validation_report(str(pdf_path), result, str(report_path))

    assert report_path.exists()
    assert "Validation report for" in report_path.read_text(encoding="utf-8")
