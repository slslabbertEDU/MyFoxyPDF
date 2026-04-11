import fitz

class TextEditor:
    def __init__(self, page: fitz.Page):
        self.page = page

    def get_text_spans(self):
        """Returns all text spans with their bounding boxes and properties."""
        spans = []
        blocks = self.page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:  # text block
                for l in b["lines"]:
                    for s in l["spans"]:
                        spans.append({
                            "text": s["text"],
                            "bbox": s["bbox"],
                            "font": s["font"],
                            "size": s["size"],
                            "color": s["color"]
                        })
        return spans

    def redact_and_replace_text(self, span_bbox, new_text, fontname="helv", fontsize=11):
        """
        Redacts the original text at span_bbox and inserts new text.
        Returns True if successful.
        """
        rect = fitz.Rect(span_bbox)
        self.page.add_redact_annot(rect, fill=(1, 1, 1))
        self.page.apply_redactions()
        point = fitz.Point(rect.x0, rect.y1 - (rect.height * 0.2))
        self.page.insert_text(point, new_text, fontname=fontname, fontsize=fontsize)
        return True
