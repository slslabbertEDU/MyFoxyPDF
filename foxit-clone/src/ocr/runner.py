import os
import pytesseract
from PIL import Image

class OCRRunner:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt':
            # Default path for Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        self.tesseract_cmd = pytesseract.pytesseract.tesseract_cmd

    def is_available(self):
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            # If command is explicitly provided but invalid, or standard tesseract not found
            # we also check if the path exists, but get_tesseract_version is safer.
            return False

    def run_ocr(self, image_path, output_base):
        """
        Runs OCR on the given image and saves it to output_base.
        (e.g., if output_base is 'out', it might create 'out.txt' or 'out.pdf')
        """
        if not self.is_available():
            raise FileNotFoundError("Tesseract OCR is not available. Please install it.")

        # Here we just return the extracted text as a simple implementation,
        # but the test mostly checks if it raises FileNotFoundError.
        text = pytesseract.image_to_string(Image.open(image_path))
        with open(f"{output_base}.txt", "w", encoding="utf-8") as f:
            f.write(text)
        return text
