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
        self.list = QtWidgets.QTableWidget(0, 2)
        self.list.setHorizontalHeaderLabels(["Key", "Value"])
        self.list.horizontalHeader().setStretchLastSection(True)
        self.list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        remove = QtWidgets.QPushButton("Remove Selected")
        remove.clicked.connect(self._remove_sel)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.k)
        top.addWidget(self.v)
        top.addWidget(add)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.list)
        layout.addWidget(remove)

        store.specChanged.connect(self.refresh)
        self.refresh()

    def _add(self):
        k, v = self.k.text().strip(), self.v.text().strip()
        if not k:
            return
        self.on_add(k, v)
        self.k.clear()
        self.v.clear()

    def _remove_sel(self):
        rows = sorted({i.row() for i in self.list.selectedIndexes()}, reverse=True)
        keys = list(self.store.spec.get("default_headers", {}).keys())
        for r in rows:
            if 0 <= r < len(keys):
                self.on_remove_key(keys[r])

    def refresh(self):
        headers = self.store.spec.get("default_headers", {})
        self.list.setRowCount(len(headers))
        for i, (k, v) in enumerate(headers.items()):
            self.list.setItem(i, 0, QtWidgets.QTableWidgetItem(k))
            self.list.setItem(i, 1, QtWidgets.QTableWidgetItem(str(v)))
