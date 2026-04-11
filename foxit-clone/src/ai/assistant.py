from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QHBoxLayout

class AIAssistant(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.label = QLabel("AI Assistant (Mock)")
        self.layout.addWidget(self.label)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.layout.addWidget(self.chat_history)

        self.input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_btn = QPushButton("Send")

        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_btn)

        self.layout.addLayout(self.input_layout)

        self.send_btn.clicked.connect(self._handle_send)
        self.input_field.returnPressed.connect(self._handle_send)

    def _handle_send(self):
        text = self.input_field.text().strip()
        if text:
            # Display user message
            self.chat_history.append(f"You: {text}")
            self.input_field.clear()

            # Display mock AI response
            self.chat_history.append(f"AI: I received your message: '{text}'")
