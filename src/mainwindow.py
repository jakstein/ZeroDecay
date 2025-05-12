import sys
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLineEdit, QScrollArea,
    QLabel, QFrame, QGridLayout, QSizePolicy, QLayout, QStyle
)
from PySide6.QtCore import Qt, QSize, QPoint, QRect, QRegularExpression
from PySide6.QtGui import QPalette, QColor

# --- Custom FlowLayout ---
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, h_spacing=-1, v_spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def horizontalSpacing(self):
        if self._h_spacing >= 0:
            return self._h_spacing
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._v_spacing >= 0:
            return self._v_spacing
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0) # Not expanding

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins() # Qt6
        size += QSize(2 * margin, 2 * margin)
        return size

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.horizontalSpacing()

        for item in self._item_list:
            if not item.widget().isVisible(): # Skip hidden widgets
                continue

            next_x = x + item.sizeHint().width() + spacing
            if next_x - spacing > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + self.verticalSpacing()
                next_x = x + item.sizeHint().width() + spacing
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        return y + line_height - rect.y()


# --- UI Components ---
class HealthSquare(QFrame):
    SQUARE_SIZE = 25  # Define a consistent size for squares

    def __init__(self, is_healthy=True, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        # self.setFrameShadow(QFrame.Sunken) # A flatter look might be cleaner
        self.setAutoFillBackground(True)
        palette = self.palette()
        if is_healthy:
            palette.setColor(QPalette.Window, QColor("#4CAF50")) # A slightly nicer green
        else:
            palette.setColor(QPalette.Window, QColor("#F44336")) # A slightly nicer red
        self.setPalette(palette)
        self.setFixedSize(self.SQUARE_SIZE, self.SQUARE_SIZE) # Make squares fixed size


class FileContainerWidget(QFrame):
    MAX_SQUARES_PER_ROW = 5 # Max squares horizontally inside a container

    def __init__(self, filename, copies_status, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised) # Keep raised for container distinction
        self.setLineWidth(1)
        # self.setMinimumWidth(150) # Ensure a minimum width
        # self.setMaximumWidth(300) # Prevent excessive stretching

        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(6)

        self.filename_label = QLabel(filename)
        self.filename_label.setAlignment(Qt.AlignCenter)
        font = self.filename_label.font()
        font.setBold(True)
        self.filename_label.setFont(font)
        self.filename_label.setWordWrap(True) # Allow filename to wrap
        container_layout.addWidget(self.filename_label)

        squares_panel = QWidget()
        self.squares_layout = QGridLayout(squares_panel)
        self.squares_layout.setSpacing(4) # Spacing between squares

        row, col = 0, 0
        for is_healthy in copies_status:
            square = HealthSquare(is_healthy)
            self.squares_layout.addWidget(square, row, col)
            col += 1
            if col >= self.MAX_SQUARES_PER_ROW:
                col = 0
                row += 1
        
        # Add stretch to align squares to the top-left if fewer than MAX_SQUARES_PER_ROW
        if copies_status:
             self.squares_layout.setColumnStretch(self.MAX_SQUARES_PER_ROW, 1)
             self.squares_layout.setRowStretch(row +1 , 1)


        container_layout.addWidget(squares_panel)
        # self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def get_filename(self):
        return self.filename

    def sizeHint(self):
        # Calculate a more accurate size hint
        width = 0
        height = 0

        # Filename label
        label_hint = self.filename_label.sizeHint()
        width = max(width, label_hint.width())
        height += label_hint.height() + self.layout().spacing()

        # Squares panel
        num_copies = self.squares_layout.count()
        if num_copies > 0:
            rows = (num_copies + self.MAX_SQUARES_PER_ROW - 1) // self.MAX_SQUARES_PER_ROW
            cols = min(num_copies, self.MAX_SQUARES_PER_ROW)
            
            square_width_with_spacing = HealthSquare.SQUARE_SIZE + self.squares_layout.horizontalSpacing()
            square_height_with_spacing = HealthSquare.SQUARE_SIZE + self.squares_layout.verticalSpacing()

            squares_area_width = cols * square_width_with_spacing - self.squares_layout.horizontalSpacing()
            squares_area_height = rows * square_height_with_spacing - self.squares_layout.verticalSpacing()
            
            width = max(width, squares_area_width)
            height += squares_area_height
        
        margins = self.layout().contentsMargins()
        width += margins.left() + margins.right()
        height += margins.top() + margins.bottom()

        # Define a sensible minimum width for containers based on squares
        min_width_for_squares = self.MAX_SQUARES_PER_ROW * HealthSquare.SQUARE_SIZE + \
                                (self.MAX_SQUARES_PER_ROW -1) * self.squares_layout.spacing() + \
                                margins.left() + margins.right()
        
        return QSize(max(180, min(width,350), min_width_for_squares), height)


class MonitoringTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self) # Main layout for the tab

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files (regex supported)...")
        self.search_bar.textChanged.connect(self.filter_files)
        main_layout.addWidget(self.search_bar)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        
        # This widget will contain the FlowLayout
        self.scroll_content_widget = QWidget() 
        self.flow_layout = FlowLayout(self.scroll_content_widget, margin=10, h_spacing=10, v_spacing=10)
        # self.scroll_content_widget.setLayout(self.flow_layout) # Already set by FlowLayout parent

        scroll_area.setWidget(self.scroll_content_widget)
        main_layout.addWidget(scroll_area)

        self.file_containers_widgets = [] # Store the actual container widgets
        self.load_extensive_sample_data_for_preview()

    def load_extensive_sample_data_for_preview(self):
        sample_files = [
            ("John.json", [True] * 8),
            ("cat.jpg", [True, True, False, False, True]),
            ("lol.cs", [True, True]),
            ("document_very_long_name_that_might_wrap_around.pdf", [True] * 12),
            ("archive_with_many_issues.zip", [True, False, True, False, True, False, True, False, False, False]),
            ("image_collection_large.tar.gz", [True] * 28),
            ("another_file_mostly_healthy.txt", [True, True, True, True, False, True, True]),
            ("critical_backup.dat", [False, False, False, False]),
            ("config_system.ini", [True] * 3),
            ("research_paper_final_v2_urgent.docx", [True, True, False, True, True, False, True, True, True, False, True]),
            ("video_render_output_001.mp4", [True] * 15),
            ("source_code_module.py", [True, True, True, False, True]),
            ("temporary_file.tmp", [False]),
            ("user_settings.xml", [True]),
            ("db_export_2025_05_12_detailed_report_for_analysis.sql", [True, True, True, True, True, True, True, True, True, True, False, True, True, True, True]),
            ("presentation_slides_important_final_review_copy.pptx", [True, False, True, False, True, False]),
            ("financial_report_q1_audited_version.xlsx", [True] * 9),
            ("utility_tool_v3.exe", [True, True, False]),
            ("kernel_panic_log_archive_deep_dive.log", [True] * 22),
            ("short.txt", [True, False]),
            ("tiny.cfg", [True]),
            ("backup_set_alpha.bak", [True]*2),
            ("backup_set_beta_needs_check.bak", [True, False, True]),
            ("backup_set_gamma_all_good.bak", [True]*7),
        ]

        # Clear existing widgets from layout and list
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self.file_containers_widgets.clear()

        for filename, statuses in sample_files:
            container = FileContainerWidget(filename, statuses)
            self.flow_layout.addWidget(container) # Add widget directly to FlowLayout
            self.file_containers_widgets.append(container)
    
    def filter_files(self, text):
        try:
            regex = QRegularExpression(text, QRegularExpression.CaseInsensitiveOption)
            if not regex.isValid(): 
                safe_text = QRegularExpression.escape(text)
                regex = QRegularExpression(safe_text, QRegularExpression.CaseInsensitiveOption)
        except Exception: 
            safe_text = QRegularExpression.escape(text)
            regex = QRegularExpression(safe_text, QRegularExpression.CaseInsensitiveOption)

        for container_widget in self.file_containers_widgets:
            match = regex.match(container_widget.get_filename())
            if match.hasMatch() or not text:
                container_widget.setVisible(True)
            else:
                container_widget.setVisible(False)
        self.flow_layout.invalidate() # Important: tell the layout to update


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Duplication Monitor")
        self.setGeometry(100, 100, 1000, 750) # Wider default window

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.monitoring_tab = MonitoringTab()
        self.tab_widget.addTab(self.monitoring_tab, "Monitoring")

        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Settings") # Renamed for example
        tab2_layout = QVBoxLayout(self.tab2)
        tab2_layout.addWidget(QLabel("Application Settings and Configuration"))
        self.tab2.setLayout(tab2_layout)

        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, "Log") # Renamed for example
        tab3_layout = QVBoxLayout(self.tab3)
        tab3_layout.addWidget(QLabel("Event Log and History"))
        self.tab3.setLayout(tab3_layout)

        self.tab4 = QWidget()
        self.tab_widget.addTab(self.tab4, "About") # Renamed for example
        tab4_layout = QVBoxLayout(self.tab4)
        tab4_layout.addWidget(QLabel("About this File Monitor application."))
        self.tab4.setLayout(tab4_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())