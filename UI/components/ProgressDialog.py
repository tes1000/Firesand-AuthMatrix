"""
Progress Dialog Component

Displays a modal dialog with animated spinner and feedback text when running tests.
Includes a cancel button to stop the running process.
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..views.Theme import primary, secondary, background, text, border


class ProgressDialog(QtWidgets.QDialog):
    """
    Modal progress dialog with animated spinner and cancel functionality.

    Shows feedback to user during long-running operations like API testing.
    Provides a cancel button to terminate the operation.
    """

    # Signal emitted when user clicks cancel button
    cancelRequested = QtCore.Signal()

    def __init__(self, parent=None):
        """
        Initialize the progress dialog.

        Args:
            parent: Parent widget (typically MainWindow)
        """
        super().__init__(parent)

        # Dialog configuration
        self.setModal(True)
        self.setWindowTitle("Running Tests")
        self.setMinimumSize(400, 200)
        self.setMaximumSize(500, 250)

        # Remove window close button (X) to force use of Cancel button
        self.setWindowFlags(
            QtCore.Qt.Dialog |
            QtCore.Qt.CustomizeWindowHint |
            QtCore.Qt.WindowTitleHint
        )

        # Apply modern styling
        self._apply_stylesheet()

        # Create UI elements
        self._create_ui()

        # Animation timer for spinner
        self._rotation_angle = 0
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_spinner)

    def _create_ui(self):
        """Create the dialog UI components."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Spinner (animated circle)
        self.spinner_label = QtWidgets.QLabel()
        self.spinner_label.setAlignment(QtCore.Qt.AlignCenter)
        self.spinner_label.setFixedSize(60, 60)
        layout.addWidget(self.spinner_label, alignment=QtCore.Qt.AlignCenter)

        # Feedback text
        self.message_label = QtWidgets.QLabel("Sending requests...")
        self.message_label.setAlignment(QtCore.Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet(f"font-size: 14px; color: {text};")
        layout.addWidget(self.message_label)

        # Progress info (optional additional details)
        self.detail_label = QtWidgets.QLabel("")
        self.detail_label.setAlignment(QtCore.Qt.AlignCenter)
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.detail_label)

        layout.addStretch()

        # Cancel button
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setFixedWidth(120)
        self.cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_button, alignment=QtCore.Qt.AlignCenter)

    def _apply_stylesheet(self):
        """Apply modern stylesheet to dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {background};
                border: 1px solid {border};
                border-radius: 8px;
            }}
            QPushButton {{
                background-color: {primary};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {secondary};
            }}
            QPushButton:pressed {{
                background-color: #0056b3;
            }}
        """)

    def _create_spinner_pixmap(self):
        """
        Create a spinner pixmap with a circular arc.

        Returns:
            QPixmap: Pixmap with spinner graphic
        """
        size = 60
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw circular arc for spinner
        pen = QtGui.QPen(QtGui.QColor(primary))
        pen.setWidth(4)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)

        # Draw arc (270 degrees, leaving 90 degree gap)
        rect = QtCore.QRectF(5, 5, size - 10, size - 10)
        painter.drawArc(rect, self._rotation_angle * 16, 270 * 16)

        painter.end()
        return pixmap

    def _update_spinner(self):
        """Update spinner rotation animation."""
        self._rotation_angle = (self._rotation_angle + 10) % 360
        pixmap = self._create_spinner_pixmap()
        self.spinner_label.setPixmap(pixmap)

    def start(self):
        """Start the spinner animation and show the dialog."""
        self._timer.start(50)  # Update every 50ms for smooth animation
        self.show()

    def stop(self):
        """Stop the spinner animation and hide the dialog."""
        self._timer.stop()
        self.hide()

    def set_message(self, message: str):
        """
        Update the main feedback message.

        Args:
            message: Message text to display
        """
        self.message_label.setText(message)

    def set_detail(self, detail: str):
        """
        Update the detail/progress information.

        Args:
            detail: Detail text to display
        """
        self.detail_label.setText(detail)

    def _on_cancel(self):
        """Handle cancel button click."""
        # Disable button to prevent multiple clicks
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Cancelling...")

        # Emit signal for parent to handle cancellation
        self.cancelRequested.emit()

    def reset(self):
        """Reset dialog to initial state."""
        self._rotation_angle = 0
        self.cancel_button.setEnabled(True)
        self.cancel_button.setText("Cancel")
        self.set_message("Sending requests...")
        self.set_detail("")

    def closeEvent(self, event):
        """
        Handle dialog close event.

        Prevent closing via window manager, force use of Cancel button.
        """
        # Ignore close event - user must click Cancel
        event.ignore()
