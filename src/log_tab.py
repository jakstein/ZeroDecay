from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class LogTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.logDisplay = QTextEdit()
        self.logDisplay.setReadOnly(True)
        layout.addWidget(self.logDisplay)
        self.setLayout(layout)

    def addLog(self, message: str):
        self.logDisplay.append(message)