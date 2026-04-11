import fitz

def apply_redaction(page: fitz.Page, rect_coords: tuple):
    rect = fitz.Rect(rect_coords)
    # Add a redaction annotation
    page.add_redact_annot(rect, fill=(0, 0, 0)) # Fill with black (traditional redaction)
    # Apply the redaction
    page.apply_redactions()
