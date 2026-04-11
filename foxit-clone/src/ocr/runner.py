import os
import subprocess

class OCRRunner:
    def __init__(self, tesseract_cmd: str = "tesseract"):
        self.tesseract_cmd = tesseract_cmd

    def is_available(self) -> bool:
        try:
            # Running with --version is a good way to check if it's installed and accessible
            subprocess.run([self.tesseract_cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def run_ocr(self, image_path: str, output_base: str, lang: str = "eng"):
        if not self.is_available():
            raise FileNotFoundError(f"Tesseract command '{self.tesseract_cmd}' not found or not executable.")

        # Run tesseract image_path output_base -l lang
        subprocess.run([self.tesseract_cmd, image_path, output_base, "-l", lang], check=True)
