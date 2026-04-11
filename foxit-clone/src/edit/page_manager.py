import fitz

class PageManager:
    def __init__(self, doc: fitz.Document):
        self.doc = doc

    def insert_empty_page(self, at: int = -1):
        """Inserts an empty page at the specified index."""
        self.doc.new_page(at)

    def delete_page(self, index: int) -> bool:
        """Deletes a page at the specified index."""
        if 0 <= index < len(self.doc):
            self.doc.delete_page(index)
            return True
        return False

    def rotate_page(self, index: int, angle: int):
        """Rotates the page at the given index by the specified angle."""
        if 0 <= index < len(self.doc):
            page = self.doc[index]
            page.set_rotation(angle)

    def merge_pdf(self, path: str):
        """Merges another PDF file into this document."""
        other_doc = fitz.open(path)
        self.doc.insert_pdf(other_doc)
        other_doc.close()
