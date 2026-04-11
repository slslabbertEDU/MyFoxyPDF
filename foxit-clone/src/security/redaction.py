import fitz

def apply_redaction(page: fitz.Page, rect):
    """
    Adds a redaction annotation and immediately applies it to black out the text.

    :param page: The fitz.Page object.
    :param rect: The bounding box for the redaction (e.g. tuple (x0, y0, x1, y1)).
    """
    # Create the redaction annotation
    annot = page.add_redact_annot(rect, text="REDACTED", cross_out=True)
    annot.update()

    # Apply all redactions on the page
    page.apply_redactions()
