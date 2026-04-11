import fitz

def add_highlight(page, rect):
    """
    Adds a highlight annotation to the given page at the specified rectangle.

    :param page: fitz.Page object representing the PDF page.
    :param rect: A tuple or fitz.Rect representing the coordinates (x0, y0, x1, y1).
    """
    fitz_rect = fitz.Rect(rect)
    annot = page.add_highlight_annot(fitz_rect)
    annot.update()
