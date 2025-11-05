from typing import Tuple
from PySide6 import QtWidgets


def multiline_input(parent: QtWidgets.QWidget, title: str, label: str) -> Tuple[str, bool]:
    """Show a dialog for multiline text input."""
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle(title)
    lay = QtWidgets.QVBoxLayout(dlg)
    lay.addWidget(QtWidgets.QLabel(label))
    edit = QtWidgets.QPlainTextEdit()
    edit.setMinimumSize(700, 420)
    lay.addWidget(edit)
    btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    lay.addWidget(btns)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    ok = dlg.exec() == QtWidgets.QDialog.Accepted
    return edit.toPlainText(), ok


def show_text(parent: QtWidgets.QWidget, title: str, text: str) -> None:
    """Show a dialog with read-only text content."""
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle(title)
    lay = QtWidgets.QVBoxLayout(dlg)
    edit = QtWidgets.QPlainTextEdit()
    edit.setReadOnly(True)
    edit.setPlainText(text)
    edit.setMinimumSize(700, 500)
    lay.addWidget(edit)
    btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
    lay.addWidget(btns)
    btns.rejected.connect(dlg.reject)
    btns.accepted.connect(dlg.accept)
    btns.button(QtWidgets.QDialogButtonBox.Close).setText("Close")
    dlg.exec()
