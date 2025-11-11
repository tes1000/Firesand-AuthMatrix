import os
from PySide6 import QtCore, QtGui, QtWidgets
from ..views.Theme import banner, topbar, primary, lines, fg1
from ..views.ModernStyles import get_header_stylesheet, apply_animation_properties


class LogoHeader(QtWidgets.QWidget):
    """Header with logo, project name, theme color, Import/Export/Run buttons."""
    runRequested = QtCore.Signal()
    importRequested = QtCore.Signal()
    exportRequested = QtCore.Signal()
    themeColorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(135)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, True)

        # Load banner once
        self._banner = self._load_banner()
        # Use theme primary color as background
        self._bg = QtGui.QColor(banner)

        # Apply modern header stylesheet
        self.setStyleSheet(get_header_stylesheet())

        # --- UI ---
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
        self.runBtn.clicked.connect(self.runRequested.emit)

        left = QtWidgets.QHBoxLayout()
        left.addWidget(self.nameEdit)
        left.addStretch(1)
        
        right = QtWidgets.QHBoxLayout()
        right.addStretch(1)
        right.addWidget(self.importBtn)
        right.addWidget(self.exportBtn)
        right.addWidget(self.runBtn)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addLayout(left)
        layout.addLayout(right)

    def paintEvent(self, ev: QtGui.QPaintEvent) -> None:
        # 1) Fill header with theme primary color
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), self._bg)

        # 2) Draw banner centered, preserving aspect ratio
        if self._banner and not self._banner.isNull():
            # Scale to header height only, keep aspect ratio
            pix = self._banner
            if pix.height() > 0 and self.height() > 0:
                pix = self._banner.scaledToHeight(self.height(),
                                                  QtCore.Qt.SmoothTransformation)

            x = (self.width()  - pix.width())  // 2
            y = (self.height() - pix.height()) // 2
            p.drawPixmap(x, y, pix)

    def _load_banner(self) -> QtGui.QPixmap:
        banner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "banner.jpg")
        pm = QtGui.QPixmap(banner_path)
        if pm.isNull():
            print("Banner not found or failed to load:", banner_path)
        return pm
