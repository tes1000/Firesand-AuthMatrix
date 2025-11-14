import os
from PySide6 import QtCore, QtGui, QtWidgets
from ..views.Theme import banner
from ..views.ModernStyles import get_header_stylesheet, apply_animation_properties


class LogoHeader(QtWidgets.QWidget):
    """Header with logo, project name, theme color, Import/Export/Run buttons."""
    runRequested = QtCore.Signal()
    stopRequested = QtCore.Signal()
    importRequested = QtCore.Signal()
    exportRequested = QtCore.Signal()
    themeColorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)
        self.is_running = False

        # Apply modern header stylesheet
        self.setStyleSheet(get_header_stylesheet())

        # Load logo once and scale it to fixed size
        logo_pixmap = self._load_logo()

        # --- UI ---
        self.logoLabel = QtWidgets.QLabel()
        self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        if not logo_pixmap.isNull():
            # Scale logo to fixed height of 80px
            scaled_logo = logo_pixmap.scaledToHeight(130, QtCore.Qt.SmoothTransformation)
            self.logoLabel.setPixmap(scaled_logo)
            self.logoLabel.setFixedSize(scaled_logo.size())

        self.nameEdit = QtWidgets.QLineEdit(placeholderText="Project Name (UI only)")
        self.nameEdit.setMinimumWidth(220)
        apply_animation_properties(self.nameEdit)

        self.importBtn = QtWidgets.QPushButton("Import")
        self.exportBtn = QtWidgets.QPushButton("Export")
        self.runBtn = QtWidgets.QPushButton("Run")
        self.runBtn.setDefault(True)

        # Apply animation properties to buttons
        for btn in (self.importBtn, self.exportBtn, self.runBtn):
            apply_animation_properties(btn)

        self.importBtn.clicked.connect(self.importRequested.emit)
        self.exportBtn.clicked.connect(self.exportRequested.emit)
        self.runBtn.clicked.connect(self._on_run_stop_clicked)

        # Spinner label for inline animation (initially hidden)
        self.spinnerLabel = QtWidgets.QLabel()
        self.spinnerLabel.setFixedSize(16, 16)
        self.spinnerLabel.hide()

        # Timer for spinner animation
        self._rotation_angle = 0
        self._spinner_timer = QtCore.QTimer(self)
        self._spinner_timer.timeout.connect(self._update_spinner)

        left = QtWidgets.QHBoxLayout()
        left.addWidget(self.nameEdit)
        left.addStretch(1)

        # Center logo
        center = QtWidgets.QHBoxLayout()
        center.addStretch(1)
        center.addWidget(self.logoLabel)
        center.addStretch(1)

        # Right layout with spinner after run button
        right = QtWidgets.QHBoxLayout()
        right.addStretch(1)
        right.addWidget(self.importBtn)
        right.addWidget(self.exportBtn)
        right.addWidget(self.runBtn)
        right.addSpacing(8)  # Add spacing between Run button and spinner
        right.addWidget(self.spinnerLabel)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)  # Logo margins
        layout.addLayout(left, 1)
        layout.addLayout(center, 1)
        layout.addLayout(right, 1)

    def _load_logo(self) -> QtGui.QPixmap:
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
        )

        for filename in ("firesand_logo.png", "Logo_Ai.png", "banner.jpg"):
            logo_path = os.path.join(assets_dir, filename)
            pixmap = QtGui.QPixmap(logo_path)
            if not pixmap.isNull():
                return pixmap

        print("Logo not found in assets directory.")
        return QtGui.QPixmap()

    def _on_run_stop_clicked(self):
        """Handle Run/Stop button click"""
        if self.is_running:
            self.stopRequested.emit()
        else:
            self.runRequested.emit()

    def set_running_state(self, running: bool):
        """Set the button to Running (Stop) or Ready (Run) state"""
        self.is_running = running
        if running:
            self.runBtn.setText("Stop")
            self.spinnerLabel.show()
            self._spinner_timer.start(50)  # 20 FPS
        else:
            self.runBtn.setText("Run")
            self.spinnerLabel.hide()
            self._spinner_timer.stop()

    def _create_spinner_pixmap(self):
        """Create a small spinner pixmap with a circular arc"""
        size = 16
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw circular arc for spinner
        pen = QtGui.QPen(QtGui.QColor("#CE2929"))  # Primary red color
        pen.setWidth(2)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Draw arc (270 degrees, leaving 90 degree gap)
        rect = QtCore.QRectF(2, 2, size - 4, size - 4)
        painter.drawArc(rect, self._rotation_angle * 16, 270 * 16)

        painter.end()
        return pixmap

    def _update_spinner(self):
        """Update spinner rotation animation"""
        self._rotation_angle = (self._rotation_angle + 10) % 360
        pixmap = self._create_spinner_pixmap()
        self.spinnerLabel.setPixmap(pixmap)
