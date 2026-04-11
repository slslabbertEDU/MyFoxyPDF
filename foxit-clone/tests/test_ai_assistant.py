import pytest
import os
import sys
from PySide6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from ai.assistant import AIAssistant

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_ai_assistant_init(qapp):
    assistant = AIAssistant()
    assert assistant.label.text() == "AI Assistant (Mock)"

    assistant.input_field.setText("What is this PDF?")
    assistant.send_btn.click()
    assert "What is this PDF?" in assistant.chat_history.toPlainText()
