import fitz

class PageManager:
    def __init__(self, doc: fitz.Document):
        self.doc = doc

    def insert_empty_page(self, index: int = -1):
        self.doc.new_page(index)

    def delete_page(self, index: int) -> bool:
        if 0 <= index < len(self.doc):
            self.doc.delete_page(index)
            return True
        return False

    def rotate_page(self, index: int, rotation: int):
        if 0 <= index < len(self.doc):
            page = self.doc[index]
            page.set_rotation(rotation)

    def merge_pdf(self, filepath: str):
        other_doc = fitz.open(filepath)
        self.doc.insert_pdf(other_doc)
        other_doc.close()
