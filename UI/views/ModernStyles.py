"""
Modern stylesheet system for Firesand Auth Matrix
Provides responsive, animated, and professional UI styles
"""

from .Theme import (
    bg1, bg2, topbar, fg1, fg2,
    primary, primary_dark, primary_light,
    secondary, secondary_dark,
    success, warning, danger, info,
    accent, alt_bg1, alt_bg2, alt_fg2,
    lines, border_color, hover_bg, btn_default_bg,
    high_emphasis, medium_emphasis, disabled
)


def get_main_stylesheet() -> str:
    """
    Get the main application stylesheet with modern design and animations.
    Includes hover effects, transitions, and responsive styling.
    """
    return f"""
    /* Global Application Styles */
    QWidget {{
        background-color: {bg1};
        color: {fg1};
        font-family: "Segoe UI", "Roboto", "Ubuntu", "Helvetica Neue", Arial, sans-serif;
        font-size: 13px;
    }}
    
    /* Main Window */
    QMainWindow {{
        background-color: {bg1};
    }}
    
    /* Buttons - Modern with hover and press effects */
    QPushButton {{
        background-color: {btn_default_bg};
        color: {fg1};
        border: 1px solid {lines};
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 500;
        min-height: 28px;
    }}
    
    QPushButton:hover {{
        background-color: {hover_bg};
        border: 1px solid {alt_fg2};
    }}
    
    QPushButton:pressed {{
        background-color: {alt_bg1};
        padding-top: 9px;
        padding-bottom: 7px;
    }}
    
    QPushButton:disabled {{
        background-color: {bg2};
        color: {disabled};
        border: 1px solid {lines};
    }}
    
    QPushButton:default {{
        background-color: {primary};
        border: 1px solid {primary_dark};
        font-weight: 600;
    }}
    
    QPushButton:default:hover {{
        background-color: {primary_light};
        border: 1px solid {primary};
    }}
    
    QPushButton:default:pressed {{
        background-color: {primary_dark};
    }}
    
    /* Primary Action Buttons */
    QPushButton[class="primary"] {{
        background-color: {primary};
        border: 1px solid {primary_dark};
        color: {fg1};
        font-weight: 600;
    }}
    
    QPushButton[class="primary"]:hover {{
        background-color: {primary_light};
    }}
    
    /* Secondary Action Buttons */
    QPushButton[class="secondary"] {{
        background-color: {secondary};
        border: 1px solid {secondary_dark};
        color: {topbar};
        font-weight: 600;
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {secondary_dark};
        color: {fg1};
    }}
    
    /* Success Buttons */
    QPushButton[class="success"] {{
        background-color: {success};
        border: 1px solid {success};
        color: {fg1};
    }}
    
    /* Warning Buttons */
    QPushButton[class="warning"] {{
        background-color: {warning};
        border: 1px solid {warning};
        color: {fg1};
    }}
    
    /* Danger Buttons */
    QPushButton[class="danger"] {{
        background-color: {danger};
        border: 1px solid {danger};
        color: {fg1};
    }}
    
    /* Text Input Fields */
    QLineEdit {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 2px solid {lines};
        border-radius: 6px;
        padding: 8px 12px;
        selection-background-color: {primary};
        min-height: 24px;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {primary};
        background-color: {bg2};
    }}
    
    QLineEdit:hover {{
        border: 2px solid {hover_bg};
    }}
    
    QLineEdit:disabled {{
        background-color: {bg2};
        color: {disabled};
        border: 2px solid {lines};
    }}
    
    QLineEdit[placeholderText] {{
        color: {medium_emphasis};
    }}
    
    /* Text Edit / Multi-line */
    QTextEdit, QPlainTextEdit {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 2px solid {lines};
        border-radius: 6px;
        padding: 8px;
        selection-background-color: {primary};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 2px solid {primary};
        background-color: {bg2};
    }}
    
    /* ComboBox */
    QComboBox {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 2px solid {lines};
        border-radius: 6px;
        padding: 8px 12px;
        min-height: 24px;
    }}
    
    QComboBox:hover {{
        border: 2px solid {hover_bg};
        background-color: {hover_bg};
    }}
    
    QComboBox:focus {{
        border: 2px solid {primary};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {fg1};
        margin-right: 8px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 2px solid {lines};
        selection-background-color: {primary};
        selection-color: {fg1};
        outline: none;
    }}
    
    /* Labels */
    QLabel {{
        color: {fg1};
        background-color: transparent;
    }}
    
    QLabel[class="title"] {{
        font-size: 18px;
        font-weight: 600;
        color: {high_emphasis};
    }}
    
    QLabel[class="subtitle"] {{
        font-size: 14px;
        font-weight: 500;
        color: {medium_emphasis};
    }}
    
    /* Tabs */
    QTabWidget::pane {{
        border: 1px solid {lines};
        background-color: {bg1};
        border-radius: 6px;
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {bg2};
        color: {medium_emphasis};
        padding: 12px 24px;
        border: 1px solid {lines};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 2px;
        min-width: 80px;
    }}
    
    QTabBar::tab:hover {{
        background-color: {hover_bg};
        color: {fg1};
    }}
    
    QTabBar::tab:selected {{
        background-color: {primary};
        color: {fg1};
        font-weight: 600;
        border-bottom: 2px solid {primary};
    }}
    
    QTabBar::tab:!selected {{
        margin-top: 2px;
    }}
    
    /* Tables */
    QTableWidget, QTableView {{
        background-color: {bg1};
        alternate-background-color: {bg2};
        color: {fg1};
        border: 1px solid {lines};
        border-radius: 6px;
        gridline-color: {lines};
        selection-background-color: {primary};
        selection-color: {fg1};
    }}
    
    QTableWidget::item, QTableView::item {{
        padding: 8px;
        border-bottom: 1px solid {lines};
    }}
    
    QTableWidget::item:hover, QTableView::item:hover {{
        background-color: {hover_bg};
    }}
    
    QTableWidget::item:selected, QTableView::item:selected {{
        background-color: {primary};
        color: {fg1};
    }}
    
    QHeaderView::section {{
        background-color: {bg2};
        color: {high_emphasis};
        padding: 10px;
        border: none;
        border-right: 1px solid {lines};
        border-bottom: 2px solid {primary};
        font-weight: 600;
    }}
    
    QHeaderView::section:hover {{
        background-color: {hover_bg};
    }}
    
    /* ScrollBars */
    QScrollBar:vertical {{
        background-color: {bg2};
        width: 12px;
        margin: 0px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {accent};
        min-height: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {alt_bg2};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {bg2};
        height: 12px;
        margin: 0px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {accent};
        min-width: 30px;
        border-radius: 6px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {alt_bg2};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* List Widgets */
    QListWidget {{
        background-color: {bg1};
        color: {fg1};
        border: 1px solid {lines};
        border-radius: 6px;
        padding: 4px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
        margin: 2px 0px;
    }}
    
    QListWidget::item:hover {{
        background-color: {hover_bg};
    }}
    
    QListWidget::item:selected {{
        background-color: {primary};
        color: {fg1};
    }}
    
    /* GroupBox */
    QGroupBox {{
        border: 2px solid {lines};
        border-radius: 6px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
        color: {high_emphasis};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: {bg1};
        left: 12px;
    }}
    
    /* ToolBar */
    QToolBar {{
        background-color: {topbar};
        border: none;
        padding: 4px;
        spacing: 8px;
    }}
    
    QToolBar::separator {{
        background-color: {lines};
        width: 1px;
        margin: 4px 8px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {bg2};
        color: {medium_emphasis};
        border-top: 1px solid {lines};
        padding: 4px 8px;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    /* Dialogs */
    QDialog {{
        background-color: {bg1};
        color: {fg1};
    }}
    
    /* Message Box */
    QMessageBox {{
        background-color: {bg1};
    }}
    
    QMessageBox QLabel {{
        color: {fg1};
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {bg2};
        border: 1px solid {lines};
        border-radius: 6px;
        text-align: center;
        color: {fg1};
        height: 20px;
    }}
    
    QProgressBar::chunk {{
        background-color: {primary};
        border-radius: 5px;
    }}
    
    /* Tooltips */
    QToolTip {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 1px solid {primary};
        border-radius: 4px;
        padding: 6px;
    }}
    
    /* Radio Buttons */
    QRadioButton {{
        color: {fg1};
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 2px solid {lines};
        background-color: {bg2};
    }}
    
    QRadioButton::indicator:hover {{
        border: 2px solid {primary};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {primary};
        border: 2px solid {primary};
    }}
    
    /* CheckBox */
    QCheckBox {{
        color: {fg1};
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 2px solid {lines};
        background-color: {bg2};
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {primary};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {primary};
        border: 2px solid {primary};
        image: url(none);
    }}
    
    /* Spin Box */
    QSpinBox, QDoubleSpinBox {{
        background-color: {alt_bg1};
        color: {fg1};
        border: 2px solid {lines};
        border-radius: 6px;
        padding: 6px;
        min-height: 24px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 2px solid {primary};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {btn_default_bg};
        border-left: 1px solid {lines};
        border-top-right-radius: 4px;
        width: 20px;
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
        background-color: {hover_bg};
    }}
    
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {btn_default_bg};
        border-left: 1px solid {lines};
        border-bottom-right-radius: 4px;
        width: 20px;
    }}
    
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {hover_bg};
    }}
    """


def get_header_stylesheet() -> str:
    """Get stylesheet for the header/toolbar section."""
    return f"""
        QWidget {{
            background-color: {topbar};
        }}
        
        QLineEdit {{
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid {lines};
            border-radius: 6px;
            padding: 8px 12px;
            color: #333;
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {primary};
            background-color: rgba(255, 255, 255, 1.0);
        }}
        
        QPushButton {{
            background-color: rgba(255, 255, 255, 0.9);
            border: 2px solid {lines};
            border-radius: 6px;
            padding: 10px 20px;
            color: #333;
            font-weight: 600;
            font-size: 13px;
        }}
        
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 1.0);
            border: 2px solid {primary};
        }}
        
        QPushButton:pressed {{
            background-color: {primary};
            color: {fg1};
        }}
    """


def apply_animation_properties(widget):
    """
    Apply animation-friendly properties to a widget.
    This enables smooth property animations for Qt widgets.
    """
    from PySide6 import QtCore
    
    # Enable hover events for animations
    widget.setAttribute(QtCore.Qt.WA_Hover, True)
    
    # Enable mouse tracking for better hover effects
    widget.setMouseTracking(True)
