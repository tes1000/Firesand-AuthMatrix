from PySide6 import QtWidgets
from .SpecStore import SpecStore

class TokensSection(QtWidgets.QWidget):
    """Add roles/tokens for authentication."""
    def __init__(self, store: SpecStore, parent=None):
        super().__init__(parent)
        self.store = store

        self.roleEdit = QtWidgets.QLineEdit(placeholderText="Role/Name (e.g., admin)")
        self.authCombo = QtWidgets.QComboBox(); self.authCombo.addItems(["Auth: none", "Auth: bearer"])
        self.tokenEdit = QtWidgets.QLineEdit(placeholderText="Bearer token (optional)")
        self.tokenEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.authCombo.currentTextChanged.connect(lambda t: self.tokenEdit.setEnabled("bearer" in t.lower()))

        addBtn = QtWidgets.QPushButton("Add Token/Role")
        addBtn.clicked.connect(self._add_role)

        top = QtWidgets.QGridLayout()
        top.addWidget(self.roleEdit,       0, 0)
        top.addWidget(self.authCombo,      0, 1)
        top.addWidget(self.tokenEdit,      0, 2)
        top.addWidget(addBtn,              0, 3)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Role", "Auth", "Token"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        delBtn = QtWidgets.QPushButton("Remove Selected")
        delBtn.clicked.connect(self._remove_selected)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)
        layout.addWidget(delBtn)

        store.specChanged.connect(self.refresh)
        self.tokenEdit.setEnabled(False)
        self.refresh()

    def _add_role(self):
        ok, err = self.store.add_role(
            self.roleEdit.text(),
            self.authCombo.currentText(),
            self.tokenEdit.text(),
        )
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Add Role", err or "Failed")
            return
        self.roleEdit.clear(); self.tokenEdit.clear()

    def _remove_selected(self):
        roles = list(self.store.spec.get("roles", {}).keys())
        rows = sorted({i.row() for i in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            if 0 <= r < len(roles):
                self.store.remove_role(roles[r])

    def refresh(self):
        roles = self.store.spec.get("roles", {})
        self.table.setRowCount(len(roles))
        for i, (rid, rdata) in enumerate(roles.items()):
            auth = rdata.get("auth", {})
            at = auth.get("type","none")
            tok = auth.get("token","") if at == "bearer" else ""
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(rid))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(at))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(tok))
