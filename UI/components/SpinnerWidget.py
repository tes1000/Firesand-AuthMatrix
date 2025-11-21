"""
Reusable spinner widget for loading indicators
"""
from PySide6 import QtCore, QtGui, QtWidgets


class SpinnerWidget(QtWidgets.QLabel):
    """
    A small animated spinner widget that shows a rotating circular arc.
    
    This widget is designed to be embedded in table cells or other UI elements
    to indicate loading/pending state.
    """
    
    def __init__(self, size: int = 16, parent=None):
        """
        Initialize the spinner widget.
        
        Args:
            size: Diameter of the spinner in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.setAlignment(QtCore.Qt.AlignCenter)
        
        # Rotation angle for animation
        self._rotation_angle = 0
        
        # Timer for animation
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._update_rotation)
        
        # Primary color for spinner (matches theme)
        self._color = QtGui.QColor("#CE2929")
        
        # Initial pixmap
        self._update_pixmap()
    
    def start(self):
        """Start the spinner animation"""
        self._timer.start(50)  # 20 FPS
    
    def stop(self):
        """Stop the spinner animation"""
        self._timer.stop()
    
    def isRunning(self) -> bool:
        """Check if spinner is currently animating"""
        return self._timer.isActive()
    
    def setColor(self, color: QtGui.QColor):
        """Set the spinner color"""
        self._color = color
        self._update_pixmap()
    
    def _update_rotation(self):
        """Update rotation angle and redraw"""
        self._rotation_angle = (self._rotation_angle + 10) % 360
        self._update_pixmap()
    
    def _update_pixmap(self):
        """Create and set the spinner pixmap"""
        pixmap = self._create_spinner_pixmap()
        self.setPixmap(pixmap)
    
    def _create_spinner_pixmap(self) -> QtGui.QPixmap:
        """Create a spinner pixmap with a circular arc"""
        pixmap = QtGui.QPixmap(self.size, self.size)
        pixmap.fill(QtCore.Qt.transparent)
        
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw circular arc
        pen = QtGui.QPen(self._color)
        pen.setWidth(2)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw arc (270 degrees, leaving 90 degree gap)
        margin = 2
        rect = QtCore.QRectF(margin, margin, self.size - 2*margin, self.size - 2*margin)
        painter.drawArc(rect, self._rotation_angle * 16, 270 * 16)
        
        painter.end()
        return pixmap
    
    def showEvent(self, event):
        """Start animation when widget becomes visible"""
        super().showEvent(event)
        if not self.isRunning():
            self.start()
    
    def hideEvent(self, event):
        """Stop animation when widget becomes hidden"""
        super().hideEvent(event)
        self.stop()
