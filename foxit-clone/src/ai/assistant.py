from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton

class AIAssistant(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel("AI Assistant (Mock)")
        layout.addWidget(self.label)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question about the PDF...")
        layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.handle_send)
        layout.addWidget(self.send_btn)

    def handle_send(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_history.append(f"You: {text}")
            self.chat_history.append("AI: I am a mock AI. I see your message.")
            self.input_field.clear()
