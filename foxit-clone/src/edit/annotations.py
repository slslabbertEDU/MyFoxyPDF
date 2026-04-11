import fitz

def add_highlight(page: fitz.Page, rect: tuple):
    """
    Adds a highlight annotation to a PyMuPDF Page.
    rect: (x0, y0, x1, y1) in PDF coordinates.
    """
    fitz_rect = fitz.Rect(rect)
    annot = page.add_highlight_annot(fitz_rect)
    annot.update()
    return annot
