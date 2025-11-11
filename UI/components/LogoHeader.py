import os
from PySide6 import QtCore, QtGui, QtWidgets
from ..views.Theme import banner
from ..views.ModernStyles import get_header_stylesheet, apply_animation_properties


class LogoHeader(QtWidgets.QWidget):
    """Header with logo, project name, theme color, Import/Export/Run buttons."""
    runRequested = QtCore.Signal()
    importRequested = QtCore.Signal()
    exportRequested = QtCore.Signal()
    themeColorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setMaximumHeight(160)

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
        self.runBtn.clicked.connect(self.runRequested.emit)

        left = QtWidgets.QHBoxLayout()
        left.addWidget(self.nameEdit)
        left.addStretch(1)
        
        # Center logo
        center = QtWidgets.QHBoxLayout()
        center.addStretch(1)
        center.addWidget(self.logoLabel)
        center.addStretch(1)
        
        right = QtWidgets.QHBoxLayout()
        right.addStretch(1)
        right.addWidget(self.importBtn)
        right.addWidget(self.exportBtn)
        right.addWidget(self.runBtn)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0) ## Logo margins
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
