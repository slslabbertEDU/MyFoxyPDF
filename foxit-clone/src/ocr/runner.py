import subprocess
import os

class OCRRunner:
    def __init__(self, tesseract_cmd="tesseract"):
        self.tesseract_cmd = tesseract_cmd

    def is_available(self):
        try:
            subprocess.run([self.tesseract_cmd, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_ocr(self, image_path, output_base, lang="eng"):
        if not self.is_available():
            raise FileNotFoundError("Tesseract is not installed or not in PATH.")

        cmd = [self.tesseract_cmd, image_path, output_base, "-l", lang, "pdf"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"OCR failed: {result.stderr}")

        return f"{output_base}.pdf"
