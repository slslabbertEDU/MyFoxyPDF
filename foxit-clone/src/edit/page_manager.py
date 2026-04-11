import fitz

class PageManager:
    def __init__(self, doc: fitz.Document):
        self.doc = doc

    def insert_empty_page(self, at_index: int = -1):
        self.doc.new_page(at_index)

    def delete_page(self, index: int):
        if 0 <= index < len(self.doc):
            self.doc.delete_page(index)
            return True
        return False

    def rotate_page(self, index: int, rotation: int = 90):
        if 0 <= index < len(self.doc):
            page = self.doc[index]
            page.set_rotation((page.rotation + rotation) % 360)
            return True
        return False

    def merge_pdf(self, other_pdf_path: str, at_index: int = -1):
        other_doc = fitz.open(other_pdf_path)
        self.doc.insert_pdf(other_doc, start_at=at_index)
        other_doc.close()
