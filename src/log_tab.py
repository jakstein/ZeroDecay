\
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class LogTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Event Log and History"))
        self.setLayout(layout)
