\
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QScrollArea,
    QLabel, QFrame, QGridLayout, QLayout, QStyle, QPushButton, QHBoxLayout
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
        return Qt.Orientation(0) # not expanding

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
        margin, _, _, _ = self.getContentsMargins()
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
            if not item.widget().isVisible(): #s kip hidden widgets
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
    SQUARE_SIZE = 25  # define a consistent size for squares

    def __init__(self, isHealthy=True, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)
        palette = self.palette()
        if isHealthy:
            palette.setColor(QPalette.Window, QColor("#4CAF50"))
        else:
            palette.setColor(QPalette.Window, QColor("#F44336"))
        self.setPalette(palette)
        self.setFixedSize(self.SQUARE_SIZE, self.SQUARE_SIZE)


class FileContainerWidget(QFrame):
    MAX_SQUARES_PER_ROW = 5 # max squares horizontally inside a container

    def __init__(self, filename, copies_status, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)

        containerLayout = QVBoxLayout(self)
        containerLayout.setContentsMargins(8, 8, 8, 8)
        containerLayout.setSpacing(6)

        self.filenameLabel = QLabel(filename)
        self.filenameLabel.setAlignment(Qt.AlignCenter)
        font = self.filenameLabel.font()
        font.setBold(True)
        self.filenameLabel.setFont(font)
        self.filenameLabel.setWordWrap(True)
        containerLayout.addWidget(self.filenameLabel)

        squares_panel = QWidget()
        self.squaresLayout = QGridLayout(squares_panel)
        self.squaresLayout.setSpacing(4)

        row, col = 0, 0
        for isHealthy in copies_status:
            square = HealthSquare(isHealthy)
            self.squaresLayout.addWidget(square, row, col)
            col += 1
            if col >= self.MAX_SQUARES_PER_ROW:
                col = 0
                row += 1
        
        if copies_status:
             self.squaresLayout.setColumnStretch(self.MAX_SQUARES_PER_ROW, 1)
             self.squaresLayout.setRowStretch(row +1 , 1)

        containerLayout.addWidget(squares_panel)

        # buttons Layout
        buttonsLayout = QHBoxLayout()
        buttonsLayout.setSpacing(5)

        self.deleteButton = QPushButton("X")
        self.deleteButton.setFixedSize(25, 25)
        self.deleteButton.clicked.connect(self.on_delete_clicked)
        buttonsLayout.addWidget(self.deleteButton)

        self.exportButton = QPushButton("↓")
        self.exportButton.setFixedSize(25, 25)
        self.exportButton.clicked.connect(self.on_export_clicked)
        buttonsLayout.addWidget(self.exportButton)

        self.scaleButton = QPushButton("S")
        self.scaleButton.setFixedSize(25, 25)
        self.scaleButton.clicked.connect(self.on_scale_clicked)
        buttonsLayout.addWidget(self.scaleButton)

        self.verifyButton = QPushButton("V")
        self.verifyButton.setFixedSize(25, 25)
        self.verifyButton.clicked.connect(self.on_verify_clicked)
        buttonsLayout.addWidget(self.verifyButton)
        
        buttonsLayout.addStretch(1) # Push buttons to the left

        containerLayout.addLayout(buttonsLayout)


    def on_delete_clicked(self):
        print(f"Delete clicked for {self.filename}")
        # placeholder for confirmation dialog and deletion logic

    def on_export_clicked(self):
        print(f"Export clicked for {self.filename}")
        # placeholder for export logic

    def on_scale_clicked(self):
        print(f"Scale clicked for {self.filename}")
        # placeholder for scaling window logic
    
    def on_verify_clicked(self):
        print(f"Verify clicked for {self.filename}")
        # placeholder for verification logic

    def get_filename(self):
        return self.filename

    def sizeHint(self):
        width = 0
        height = 0

        labelHint = self.filenameLabel.sizeHint()
        width = max(width, labelHint.width())
        height += labelHint.height() + self.layout().spacing()

        numCopies = self.squaresLayout.count()
        if numCopies > 0:
            rows = (numCopies + self.MAX_SQUARES_PER_ROW - 1) // self.MAX_SQUARES_PER_ROW
            cols = min(numCopies, self.MAX_SQUARES_PER_ROW)
            
            squareWidthWithSpacing = HealthSquare.SQUARE_SIZE + self.squaresLayout.horizontalSpacing()
            squareHeightWithSpacing = HealthSquare.SQUARE_SIZE + self.squaresLayout.verticalSpacing()

            squaresAreaWidth = cols * squareWidthWithSpacing - self.squaresLayout.horizontalSpacing()
            squaresAreaHeight = rows * squareHeightWithSpacing - self.squaresLayout.verticalSpacing()
            
            width = max(width, squaresAreaWidth)
            height += squaresAreaHeight
        
        # add height buttons row
        buttonRowHeight = 0
        if self.deleteButton: # check if buttons are created
            buttonRowHeight = self.deleteButton.sizeHint().height() + self.layout().spacing() # Assuming all buttons have similar height
            buttonsMinWidth = self.deleteButton.width() + self.exportButton.width() + self.scaleButton.width() + self.verifyButton.width() + 2 * 5 # 2 spacings
            width = max(width, buttonsMinWidth)

        height += buttonRowHeight

        margins = self.layout().contentsMargins()
        width += margins.left() + margins.right()
        height += margins.top() + margins.bottom()

        minWidthForSquares = self.MAX_SQUARES_PER_ROW * HealthSquare.SQUARE_SIZE + \
                                (self.MAX_SQUARES_PER_ROW -1) * self.squaresLayout.spacing() + \
                                margins.left() + margins.right()
        
        return QSize(max(180, min(width,350), minWidthForSquares), height)


class MonitoringTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        mainLayout = QVBoxLayout(self)

        self.searchBar = QLineEdit()
        self.searchBar.setPlaceholderText("Search files (regex supported)...")
        self.searchBar.textChanged.connect(self.filter_files)
        mainLayout.addWidget(self.searchBar)

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        
        self.scroll_content_widget = QWidget() 
        self.flowLayout = FlowLayout(self.scroll_content_widget, margin=10, h_spacing=10, v_spacing=10)

        scrollArea.setWidget(self.scroll_content_widget)
        mainLayout.addWidget(scrollArea)

        self.fileContainersWidgets = []
        self.loadSampleData()

    def loadSampleData(self):
        sampleFiles = [
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

        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self.fileContainersWidgets.clear()

        for filename, statuses in sampleFiles:
            container = FileContainerWidget(filename, statuses)
            self.flowLayout.addWidget(container)
            self.fileContainersWidgets.append(container)
    
    def filter_files(self, text):
        try:
            regex = QRegularExpression(text, QRegularExpression.CaseInsensitiveOption)
            if not regex.isValid(): 
                safe_text = QRegularExpression.escape(text)
                regex = QRegularExpression(safe_text, QRegularExpression.CaseInsensitiveOption)
        except Exception: 
            safe_text = QRegularExpression.escape(text)
            regex = QRegularExpression(safe_text, QRegularExpression.CaseInsensitiveOption)

        for container_widget in self.fileContainersWidgets:
            match = regex.match(container_widget.get_filename())
            if match.hasMatch() or not text:
                container_widget.setVisible(True)
            else:
                container_widget.setVisible(False)
        self.flowLayout.invalidate()
