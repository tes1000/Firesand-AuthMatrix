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

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Role", "Auth", "Token", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # Role
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Auth
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)           # Token
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)             # Actions - fixed width
        self.table.setColumnWidth(3, 150)  # Actions column - fixed width for delete button
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)

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

    def _remove_role(self, role_name: str):
        """Delete a specific role"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete role '{role_name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.store.remove_role(role_name)

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
            
            # Set row height to accommodate button
            self.table.setRowHeight(i, 60)
            
            # Actions column with delete button
            actionsWidget = QtWidgets.QWidget()
            actionsLayout = QtWidgets.QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(0, 0, 0, 0)
            
            deleteBtn = QtWidgets.QPushButton("Delete")
            deleteBtn.setMinimumHeight(32)
            deleteBtn.setMinimumWidth(60)
            deleteBtn.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; padding: 6px 12px; }")
            deleteBtn.clicked.connect(lambda _=None, role=rid: self._remove_role(role))
            
            actionsLayout.addStretch()
            actionsLayout.addWidget(deleteBtn)
            actionsLayout.addStretch()
            
            self.table.setCellWidget(i, 3, actionsWidget)
