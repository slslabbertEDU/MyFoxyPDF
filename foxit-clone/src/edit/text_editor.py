import fitz

class TextEditor:
    def __init__(self, page: fitz.Page):
        self.page = page

    def get_text_spans(self):
        """
        Extracts text spans from the page.
        Returns a list of dictionaries, each containing 'bbox' and 'text'.
        """
        spans = []
        blocks = self.page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        spans.append({
                            "bbox": span["bbox"],
                            "text": span["text"]
                        })
        return spans

    def redact_and_replace_text(self, bbox, new_text: str, fontsize: int = 12):
        """
        Redacts the text at the given bbox and inserts new text at that position.
        """
        # Redact the old text
        rect = fitz.Rect(bbox)
        annot = self.page.add_redact_annot(rect)
        annot.update()
        self.page.apply_redactions()

        # Insert new text
        # Point to insert is the bottom-left of the bbox
        point = fitz.Point(rect.x0, rect.y1)
        self.page.insert_text(point, new_text, fontsize=fontsize, fontname="helv")
