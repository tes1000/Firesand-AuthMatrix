from typing import Dict, Any
from PySide6 import QtWidgets, QtCore

class ResultsSection(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.table = QtWidgets.QTableWidget(0, 1)
        self.table.setHorizontalHeaderLabels(["Endpoint"])
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        # Visual polish
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)

        # Always spread columns to fill the widget
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        hdr.setMinimumSectionSize(120)        # prevents tiny columns on narrow layouts
        hdr.setHighlightSections(False)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)

    def render(self, results: Dict[str, Dict[str, Dict[str, Any]]]):
        # Reset model (clear removes headers, so we re-apply them below)
        self.table.clear()

        if not results:
            self.table.setRowCount(0)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Endpoint"])
            return

        first_ep = next(iter(results.values()), {})
        role_order = list(first_ep.keys())
        headers = ["Endpoint"] + role_order

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(results))

        # Ensure columns stretch after the column count changes
        hdr = self.table.horizontalHeader()
        for col in range(len(headers)):
            hdr.setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        for r, (ep_name, rmap) in enumerate(results.items()):
            # Endpoint column (left-aligned)
            ep_item = QtWidgets.QTableWidgetItem(ep_name)
            ep_item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            self.table.setItem(r, 0, ep_item)

            # Role columns (centered)
            for c, rid in enumerate(role_order, start=1):
                res = rmap.get(rid, {})
                st = res.get("status", "")
                http = res.get("http", "")
                badge = "✅" if st == "PASS" else ("⏭️" if st == "SKIP" else "❌")
                text = f"{badge} {http}" if http else badge
                lat = res.get("latency_ms")
                if isinstance(lat, int):
                    text += f"  {lat}ms"

                cell = QtWidgets.QTableWidgetItem(text)
                cell.setTextAlignment(QtCore.Qt.AlignCenter)
                self.table.setItem(r, c, cell)
