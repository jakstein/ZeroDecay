\
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ImportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Import Tab"))
        self.setLayout(layout)
    