import fitz

def add_highlight(page: fitz.Page, rect_coords: tuple):
    rect = fitz.Rect(rect_coords)
    highlight = page.add_highlight_annot(rect)
    highlight.update()
