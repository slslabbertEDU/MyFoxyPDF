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
                            "color": s["color"],
                            "origin": s["origin"]
                        })
        return spans

    def find_span_at_point(self, pdf_point: tuple):
        """Finds a text span containing the given PDF coordinates."""
        point = fitz.Point(pdf_point)
        for span in self.get_text_spans():
            rect = fitz.Rect(span["bbox"])
            if rect.contains(point):
                return span
        return None

    def redact_and_replace_text(self, span_bbox, span_origin, new_text, fontname="helv", fontsize=11):
        """
        Redacts the original text at span_bbox and inserts new text.
        Requires exact matrix-compatible placement via origin points.
        """
        rect = fitz.Rect(span_bbox)
        # Apply irreversible redaction to clear the old text visual
        self.page.add_redact_annot(rect, fill=(1, 1, 1))
        self.page.apply_redactions()

        # Core Engineering Rule: Strict coordinate placement using the original span origin
        # (bottom-left point) rather than manual layout math
        point = fitz.Point(span_origin)
        self.page.insert_text(point, new_text, fontname=fontname, fontsize=fontsize)
        return True
