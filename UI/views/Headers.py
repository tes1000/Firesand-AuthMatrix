from PySide6 import QtWidgets
from .SpecStore import SpecStore

class KVRow(QtWidgets.QWidget):
    def __init__(self, on_add, on_remove_key, store: SpecStore, parent=None):
        super().__init__(parent)
        self.on_add = on_add
        self.on_remove_key = on_remove_key
        self.store = store

        self.k = QtWidgets.QLineEdit(placeholderText="Header Key")
        self.v = QtWidgets.QLineEdit(placeholderText="Header Value")
        add = QtWidgets.QPushButton("Add")
        add.clicked.connect(self._add)
        self.list = QtWidgets.QTableWidget(0, 3)
        self.list.setHorizontalHeaderLabels(["Key", "Value", "Actions"])
        header = self.list.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # Key
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)           # Value
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)             # Actions - fixed width
        self.list.setColumnWidth(2, 90)  # Actions column - fixed width for delete button
        self.list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.k)
        top.addWidget(self.v)
        top.addWidget(add)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.list)

        store.specChanged.connect(self.refresh)
        self.refresh()

    def _add(self):
        k, v = self.k.text().strip(), self.v.text().strip()
        if not k:
            return
        self.on_add(k, v)
        self.k.clear()
        self.v.clear()

    def _remove_header(self, key: str):
        """Delete a specific header by key"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete header '{key}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.on_remove_key(key)

    def refresh(self):
        headers = self.store.spec.get("default_headers", {})
        self.list.setRowCount(len(headers))
        for i, (k, v) in enumerate(headers.items()):
            self.list.setItem(i, 0, QtWidgets.QTableWidgetItem(k))
            self.list.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v)))
            
            # Set row height to accommodate button
            self.list.setRowHeight(i, 45)
            
            # Actions column with delete button
            actionsWidget = QtWidgets.QWidget()
            actionsLayout = QtWidgets.QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(0, 0, 0, 0)
            
            deleteBtn = QtWidgets.QPushButton("Delete")
            deleteBtn.setMinimumHeight(30)
            deleteBtn.setMinimumWidth(60)
            deleteBtn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; font-size: 10px; padding: 0px; margin: 0px; }")
            deleteBtn.clicked.connect(lambda _=None, key=k: self._remove_header(key))
            
            actionsLayout.addStretch()
            actionsLayout.addWidget(deleteBtn)
            actionsLayout.addStretch()
            
            self.list.setCellWidget(i, 2, actionsWidget)
