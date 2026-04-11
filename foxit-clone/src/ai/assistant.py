from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Slot

class AIAssistant(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.label = QLabel("AI Assistant (Mock)")
        self.layout.addWidget(self.label)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.layout.addWidget(self.chat_history)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask me about the PDF...")
        self.layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.on_send)
        self.layout.addWidget(self.send_btn)

    @Slot()
    def on_send(self):
        user_text = self.input_field.text().strip()
        if user_text:
            self.chat_history.append(f"<b>You:</b> {user_text}")
            self.input_field.clear()
            self.chat_history.append(f"<b>AI:</b> (Mock) I see you asked: {user_text}")
