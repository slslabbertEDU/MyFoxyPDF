import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from ai.assistant import AIAssistant


def test_ai_assistant_init():
    assistant = AIAssistant()
    assert assistant.label.text() == "AI Assistant"

    assistant.input_field.setText("What is this PDF?")
    assistant.send_btn.click()
    text = assistant.chat_history.toPlainText()
    assert "What is this PDF?" in text
    assert "open PDFs" in text
