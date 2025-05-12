import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget
)
from PySide6.QtCore import Qt

from monitoring_tab import MonitoringTab
from settings_tab import SettingsTab
from log_tab import LogTab
from import_tab import ImportTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroDecay")
        self.setGeometry(100, 100, 1000, 750)

        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.monitoring_tab = MonitoringTab()
        self.tabWidget.addTab(self.monitoring_tab, "Monitoring")

        self.tab2 = SettingsTab()
        self.tabWidget.addTab(self.tab2, "Settings")

        self.tab3 = LogTab()
        self.tabWidget.addTab(self.tab3, "Log")

        self.tab4 = ImportTab()
        self.tabWidget.addTab(self.tab4, "About")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())