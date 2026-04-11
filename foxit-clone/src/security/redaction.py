import fitz

def apply_redaction(page: fitz.Page, rect: tuple, fill_color=(0, 0, 0)):
    fitz_rect = fitz.Rect(rect)
    page.add_redact_annot(fitz_rect, fill=fill_color)
    page.apply_redactions()
    return True
