import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ocr.runner import OCRRunner

def test_ocr_runner_availability():
    runner = OCRRunner(tesseract_cmd="fake_tesseract_cmd")
    assert not runner.is_available()

def test_ocr_runner_raises_on_missing():
    runner = OCRRunner(tesseract_cmd="fake_tesseract_cmd")
    with pytest.raises(FileNotFoundError):
        runner.run_ocr("dummy.png", "out")
