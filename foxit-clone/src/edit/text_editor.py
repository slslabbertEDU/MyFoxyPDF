import fitz

class TextEditor:
    def __init__(self, page: fitz.Page):
        self.page = page

    def get_text_spans(self):
        spans = []
        blocks = self.page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        spans.append({
                            "text": span["text"],
                            "bbox": span["bbox"]
                        })
        return spans

    def redact_and_replace_text(self, bbox: tuple, new_text: str, fontsize: int = 12):
        # Add a redaction to remove old text
        rect = fitz.Rect(bbox)
        self.page.add_redact_annot(rect, fill=(1, 1, 1)) # Fill with white
        self.page.apply_redactions()

        # Insert the new text in the same place
        # Using the top-left corner of the original bbox
        point = fitz.Point(bbox[0], bbox[1] + fontsize) # Adjust Y by fontsize since fitz.Point is bottom-left for insert_text
        self.page.insert_text(point, new_text, fontname="helv", fontsize=fontsize, color=(0, 0, 0))
