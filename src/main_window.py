import sys, logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget
)
from PySide6.QtCore import Qt

from monitoring_tab import MonitoringTab
from settings_tab import SettingsTab
from log_tab import LogTab
from import_tab import ImportTab
# Configure logging

class LogHandler(logging.Handler):
    def __init__(self, logWidget):
        super().__init__()
        self.logWidget = logWidget

    def emit(self, record):
        try:
            msg = self.format(record)
            self.logWidget(msg)
        except Exception:
            self.handleError(record)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZeroDecay")
        self.setGeometry(100, 100, 1000, 750)

        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)

        self.log_tab = LogTab()
        self.configLogging()

        self.monitoring_tab = MonitoringTab()
        self.tabWidget.addTab(self.monitoring_tab, "Monitoring")

        self.import_tab = ImportTab()
        self.tabWidget.addTab(self.import_tab, "Import")

        self.settings_tab = SettingsTab()
        self.tabWidget.addTab(self.settings_tab, "Settings")

        self.tabWidget.addTab(self.log_tab, "Log")

        # DEBUG START
        logging.info("Application initialized successfully.")
        logging.warning("This is a test warning message.")
        logging.debug("This is a debug message, will only show if level is DEBUG.")
        try:
            x = 1 / 0
        except ZeroDivisionError:
            logging.error("An error occurred: Division by zero.", exc_info=True)
        # DEBUG END

    def configLogging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        for handler in logger.handlers[:]: # found in example codes, supposedly prevents duplicated logs
            logger.removeHandler(handler)
        
        logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        logHandler = LogHandler(self.log_tab.addLog)
        logHandler.setFormatter(logFormat)
        logHandler.setLevel(logging.INFO)

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormat)
        consoleHandler.setLevel(logging.DEBUG)
        logger.addHandler(consoleHandler)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())