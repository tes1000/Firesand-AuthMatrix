from __future__ import annotations
import json, sys, time, multiprocessing, pickle
from typing import Dict, Any, Optional, Callable, List
import requests

from PySide6 import QtCore, QtGui, QtWidgets
from .views.SpecStore import SpecStore
from .views.Results import ResultsSection
from .views.Theme import primary, secondary, background, text, border
from .components import LogoHeader, multiline_input, show_text, TabsComponent


def worker_process_function(runner_func, spec, result_queue, error_queue):
    """Worker function that runs in a separate process."""
    try:
        # Execute the runner function with the spec
        result = runner_func(spec)
        if not isinstance(result, dict):
            raise RuntimeError("Runner returned non-dict")
        result_queue.put(result)
    except Exception as e:
        error_queue.put(str(e))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, runner: Optional[Callable[[dict], dict]] = None):
        super().__init__()
        self.setWindowTitle("Auth Matrix")
        self.resize(920, 624)
        
        # Set window icon
        self._set_window_icon()
        
        # Center the window on the screen
        self._center_window()

        self.runner = runner or (lambda spec: {})
        self.store = SpecStore()
        self.results: Optional[Dict[str, Dict[str, Dict[str, Any]]]] = None

        # Multiprocessing attributes
        self.process: Optional[multiprocessing.Process] = None
        self.result_queue: Optional[multiprocessing.Queue] = None
        self.error_queue: Optional[multiprocessing.Queue] = None
        self.poll_timer: Optional[QtCore.QTimer] = None

        # Header
        self.header = LogoHeader()
        self.addToolBarBreak()
        tool = QtWidgets.QToolBar()
        tool.setMovable(False)
        tool.addWidget(self.header)
        self.addToolBar(QtCore.Qt.TopToolBarArea, tool)

        # Theme: use static colors from Theme.py
        self.themeColor = QtGui.QColor(primary)
        self._apply_theme(self.themeColor)

        # Content as tabs
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        vlayout = QtWidgets.QVBoxLayout(central)

        # Base URL at the top
        self.baseUrlEdit = QtWidgets.QLineEdit()
        self.baseUrlEdit.setPlaceholderText("http://localhost:3000")
        self.baseUrlEdit.textChanged.connect(self.store.set_base_url)
        vlayout.addWidget(QtWidgets.QLabel("<b>Base URL</b>"))
        vlayout.addWidget(self.baseUrlEdit)

        # Tabs for Headers, Endpoints, Tokens
        self.tabs = TabsComponent(self.store)
        vlayout.addWidget(self.tabs)

        # Convenience properties to access sections
        self.headers = self.tabs.get_headers()
        self.endpoints = self.tabs.get_endpoints()
        self.tokens = self.tabs.get_tokens()

        # Results section below tabs
        vlayout.addWidget(QtWidgets.QLabel("<b>Results</b>"))
        self.resultsView = ResultsSection()
        vlayout.addWidget(self.resultsView)

        # wire header actions
        self.header.importRequested.connect(self._import_spec)
        self.header.exportRequested.connect(self._export_spec)
        self.header.runRequested.connect(self._run)

        # Connect to spec changes to update UI
        self.store.specChanged.connect(self._on_spec_changed)

        # Initialize UI with current spec values
        self._on_spec_changed()

        # statusbar
        self.statusBar().showMessage("Ready")

        # Optional: preload example data (comment out if not wanted)
        # self._load_example()

    def _center_window(self):
        """Center the window on the primary screen"""
        # Get the primary screen
        screen = QtWidgets.QApplication.primaryScreen()
        if screen is not None:
            # Get screen geometry
            screen_geometry = screen.geometry()
            
            # Calculate center position
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            
            # Move window to calculated position
            self.move(window_geometry.topLeft())

    def _set_window_icon(self):
        """Set the window icon from assets folder"""
        import os
        from pathlib import Path
        
        # Try to find the icon file
        # When running from source
        icon_path = Path(__file__).parent / "assets" / "favicon.png"
        
        # When running from PyInstaller bundle
        if not icon_path.exists() and hasattr(sys, '_MEIPASS'):
            icon_path = Path(sys._MEIPASS) / "UI" / "assets" / "favicon.png"
        
        if icon_path.exists():
            icon = QtGui.QIcon(str(icon_path))
            self.setWindowIcon(icon)
            # Also set the application icon for taskbar
            QtWidgets.QApplication.instance().setWindowIcon(icon)

    def _on_spec_changed(self):
        """Update UI elements when the spec changes"""
        # Update base URL field without triggering textChanged signal
        base_url = self.store.spec.get("base_url", "")
        if self.baseUrlEdit.text() != base_url:
            # Temporarily disconnect signal to avoid feedback loop
            self.baseUrlEdit.textChanged.disconnect()
            self.baseUrlEdit.setText(base_url)
            self.baseUrlEdit.textChanged.connect(self.store.set_base_url)

    # Theme application (apply static colors from Theme.py)
    def _apply_theme(self, color: QtGui.QColor):
        self.themeColor = color
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background};
                color: {text};
            }}
            QPushButton {{
                background-color: {primary};
                color: {text};
                border: 1px solid {border};
                padding: 6px 10px;
                border-radius: 4px;
            }}
            QToolBar {{
                background: {background};
                border: none;
            }}
            QHeaderView::section {{
                background: {secondary};
                color: {text};
            }}
        """)

    # Import/Export
    def _import_spec(self):
        # Show import options dialog
        dialog = ImportDialog(self.store, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.statusBar().showMessage("Import completed", 3000)
        else:
            self.statusBar().showMessage("Import cancelled", 2000)

    def _has_configured_expectations(self) -> bool:
        """Check if any endpoints have configured expectations"""
        for endpoint in self.store.spec.get("endpoints", []):
            if endpoint.get("expect"):
                return True
        return False

    def _show_postman_configuration_dialog(self):
        """Show dialog to configure auth levels and behavior for imported Postman collection"""
        dialog = PostmanConfigDialog(self.store, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.statusBar().showMessage("Postman collection imported and configured", 3000)
        else:
            self.statusBar().showMessage("Postman collection imported (configuration skipped)", 3000)

    def _export_spec(self):
        # Show export options dialog
        dialog = ExportDialog(self.store, self)
        dialog.exec()

    # Run
    def _run(self):
        if not self.store.spec.get("base_url"):
            QtWidgets.QMessageBox.warning(self, "Run", "Base URL is required")
            return
        url = self.store.spec["base_url"].rstrip("/")
        self.statusBar().showMessage("Running… test on: "+ url)
        self.setEnabled(False)

        # Create multiprocessing queues for communication
        self.result_queue = multiprocessing.Queue()
        self.error_queue = multiprocessing.Queue()

        # Create and start worker process
        self.process = multiprocessing.Process(
            target=worker_process_function,
            args=(self.runner, self.store.spec, self.result_queue, self.error_queue)
        )
        self.process.start()

        # Set up timer to poll for results
        self.poll_timer = QtCore.QTimer()
        self.poll_timer.timeout.connect(self._poll_process)
        self.poll_timer.start(100)  # Poll every 100ms

    def _poll_process(self):
        """Poll the worker process for completion."""
        if not self.process:
            return

        # Check if process has finished
        if not self.process.is_alive():
            self.poll_timer.stop()
            
            # Check for errors first
            if not self.error_queue.empty():
                error_msg = self.error_queue.get()
                self._on_failed(error_msg)
            # Check for results
            elif not self.result_queue.empty():
                results = self.result_queue.get()
                self._on_finished(results)
            else:
                # Process finished but no result or error (unexpected)
                self._on_failed("Process finished unexpectedly without results")
            
            # Clean up
            self.process.join()
            self.process = None
            self.result_queue = None
            self.error_queue = None
            self.poll_timer = None

    def _on_finished(self, results: dict):
        self.results = results
        self.resultsView.render(results)
        self.setEnabled(True)
        print("DEBUG: Run finished with results:")
        self.statusBar().showMessage("Done", 3000)

    def _on_failed(self, msg: str):
        QtWidgets.QMessageBox.critical(self, "Run Failed", msg)
        self.setEnabled(True)
        self.statusBar().clearMessage()

    def closeEvent(self, event):
        """Clean up multiprocessing resources when window is closed."""
        if self.process and self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1.0)  # Wait up to 1 second
            if self.process.is_alive():
                self.process.kill()  # Force kill if still alive
        
        if self.poll_timer:
            self.poll_timer.stop()
            
        super().closeEvent(event)


class PostmanConfigDialog(QtWidgets.QDialog):
    """Dialog for configuring auth levels and behavior logic for Postman imports"""
    
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Configure Postman Collection")
        self.setModal(True)
        self.resize(640, 480)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label
        info_label = QtWidgets.QLabel(
            "Configure authorization levels and expected behavior for each endpoint.\n"
            "This will set up the auth matrix testing for your imported Postman collection."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Auth roles section
        auth_group = QtWidgets.QGroupBox("Authorization Roles")
        auth_layout = QtWidgets.QFormLayout(auth_group)
        
        # Add role button
        add_role_btn = QtWidgets.QPushButton("Add Role")
        add_role_btn.clicked.connect(self._add_role)
        auth_layout.addRow(add_role_btn)
        
        # List existing roles
        self.roles_list = QtWidgets.QListWidget()
        self._refresh_roles_list()
        auth_layout.addRow("Current Roles:", self.roles_list)
        
        layout.addWidget(auth_group)
        
        # Endpoints configuration
        endpoints_group = QtWidgets.QGroupBox("Endpoint Behavior Configuration")
        endpoints_layout = QtWidgets.QVBoxLayout(endpoints_group)
        
        # Instructions
        instructions = QtWidgets.QLabel(
            "For each endpoint, configure the expected HTTP status codes for different auth levels.\n"
            "Example: /admin endpoint might return 403 for 'guest' and 200 for 'admin'."
        )
        instructions.setWordWrap(True)
        endpoints_layout.addWidget(instructions)
        
        # Endpoints table
        self.endpoints_table = QtWidgets.QTableWidget()
        self.endpoints_table.setColumnCount(3)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint", "Method", "Configure"])
        self._refresh_endpoints_table()
        endpoints_layout.addWidget(self.endpoints_table)
        
        layout.addWidget(endpoints_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        auto_config_btn = QtWidgets.QPushButton("Auto-Configure Common Patterns")
        auto_config_btn.clicked.connect(self._auto_configure)
        button_layout.addWidget(auto_config_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("Apply Configuration")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _refresh_roles_list(self):
        self.roles_list.clear()
        for role_name, role_config in self.store.spec.get("roles", {}).items():
            auth_type = role_config.get("auth", {}).get("type", "none")
            token_info = " (with token)" if auth_type == "bearer" else ""
            self.roles_list.addItem(f"{role_name} - {auth_type}{token_info}")
    
    def _refresh_endpoints_table(self):
        endpoints = self.store.spec.get("endpoints", [])
        self.endpoints_table.setRowCount(len(endpoints))
        
        for i, endpoint in enumerate(endpoints):
            # Endpoint name
            name_item = QtWidgets.QTableWidgetItem(endpoint.get("name", ""))
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.endpoints_table.setItem(i, 0, name_item)
            
            # Method
            method_item = QtWidgets.QTableWidgetItem(endpoint.get("method", "GET"))
            method_item.setFlags(method_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.endpoints_table.setItem(i, 1, method_item)
            
            # Configure button
            config_btn = QtWidgets.QPushButton("Configure")
            config_btn.clicked.connect(lambda checked, idx=i: self._configure_endpoint(idx))
            self.endpoints_table.setCellWidget(i, 2, config_btn)
        
        self.endpoints_table.resizeColumnsToContents()
    
    def _add_role(self):
        dialog = AddRoleDialog(self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            role_name, auth_type, token = dialog.get_role_data()
            success, error = self.store.add_role(role_name, auth_type, token)
            if success:
                self._refresh_roles_list()
            else:
                QtWidgets.QMessageBox.warning(self, "Add Role", error or "Failed to add role")
    
    def _configure_endpoint(self, endpoint_index):
        dialog = EndpointConfigDialog(self.store, endpoint_index, self)
        dialog.exec()
    
    def _auto_configure(self):
        """Auto-configure common auth patterns"""
        reply = QtWidgets.QMessageBox.question(
            self, "Auto-Configure", 
            "This will set up common patterns:\n"
            "• Public endpoints (/, /health, /status) → 200 for all roles\n"
            "• Admin endpoints (/admin/*) → 403 for guest, 200 for admin\n"
            "• User endpoints (/user/*, /profile) → 403 for guest, 200 for authenticated roles\n\n"
            "Continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self._apply_auto_configuration()
    
    def _apply_auto_configuration(self):
        """Apply automatic configuration patterns"""
        public_patterns = ["/", "/health", "/status", "/info", "/version"]
        admin_patterns = ["/admin"]
        user_patterns = ["/user", "/profile", "/settings"]
        
        for i, endpoint in enumerate(self.store.spec.get("endpoints", [])):
            path = endpoint.get("path", "").lower()
            
            # Check patterns
            is_public = any(path.startswith(pattern) for pattern in public_patterns)
            is_admin = any(pattern in path for pattern in admin_patterns)
            is_user = any(pattern in path for pattern in user_patterns)
            
            # Configure expectations
            for role_name in self.store.spec.get("roles", {}):
                if is_public:
                    # Public endpoints - 200 for everyone
                    status = 200
                elif is_admin:
                    # Admin endpoints - 403 for guest, 200 for admin
                    status = 200 if role_name == "admin" else 403
                elif is_user:
                    # User endpoints - 403 for guest, 200 for authenticated
                    status = 200 if role_name != "guest" else 403
                else:
                    # Default - 200 for admin, 403 for others
                    status = 200 if role_name == "admin" else 403
                
                self.store.set_endpoint_expectation(i, role_name, status=status)


class AddRoleDialog(QtWidgets.QDialog):
    """Dialog for adding a new role"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Role")
        self.setModal(True)
        
        layout = QtWidgets.QFormLayout(self)
        
        self.name_edit = QtWidgets.QLineEdit()
        layout.addRow("Role Name:", self.name_edit)
        
        self.auth_combo = QtWidgets.QComboBox()
        self.auth_combo.addItems(["none", "bearer"])
        layout.addRow("Auth Type:", self.auth_combo)
        
        self.token_edit = QtWidgets.QLineEdit()
        self.token_edit.setPlaceholderText("Enter bearer token (if applicable)")
        layout.addRow("Token:", self.token_edit)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("Add")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addRow(button_layout)
    
    def get_role_data(self):
        return (
            self.name_edit.text().strip(),
            self.auth_combo.currentText(),
            self.token_edit.text().strip()
        )


class EndpointConfigDialog(QtWidgets.QDialog):
    """Dialog for configuring individual endpoint expectations"""
    
    def __init__(self, store, endpoint_index, parent=None):
        super().__init__(parent)
        self.store = store
        self.endpoint_index = endpoint_index
        
        endpoint = store.spec["endpoints"][endpoint_index]
        self.setWindowTitle(f"Configure: {endpoint.get('name', '')}")
        self.setModal(True)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Endpoint info
        info_label = QtWidgets.QLabel(f"Endpoint: {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
        layout.addWidget(info_label)
        
        # Role expectations
        self.role_configs = {}
        for role_name in store.spec.get("roles", {}):
            group = QtWidgets.QGroupBox(f"Role: {role_name}")
            group_layout = QtWidgets.QFormLayout(group)
            
            # Status code
            status_edit = QtWidgets.QLineEdit()
            current_expect = endpoint.get("expect", {}).get(role_name, {})
            if "status" in current_expect:
                status_edit.setText(str(current_expect["status"]))
            else:
                status_edit.setPlaceholderText("e.g., 200, 403, [200,201]")
            
            group_layout.addRow("Expected Status:", status_edit)
            
            self.role_configs[role_name] = {"status": status_edit}
            layout.addWidget(group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("Save")
        ok_btn.clicked.connect(self._save_config)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _save_config(self):
        """Save the configuration for this endpoint"""
        for role_name, widgets in self.role_configs.items():
            status_text = widgets["status"].text().strip()
            if status_text:
                try:
                    # Try to parse as int first, then as list
                    if status_text.startswith("[") and status_text.endswith("]"):
                        status = json.loads(status_text)
                    else:
                        status = int(status_text)
                    
                    self.store.set_endpoint_expectation(self.endpoint_index, role_name, status=status)
                except (ValueError, json.JSONDecodeError):
                    QtWidgets.QMessageBox.warning(self, "Invalid Status", f"Invalid status code for {role_name}: {status_text}")
                    return
        
        self.accept()


class ExportDialog(QtWidgets.QDialog):
    """Dialog for exporting in different formats"""
    
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Export Specification")
        self.setModal(True)
        self.resize(320, 160)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        label = QtWidgets.QLabel("Choose export format:")
        layout.addWidget(label)
        
        # Export options
        authmatrix_btn = QtWidgets.QPushButton("Export as AuthMatrix Format")
        authmatrix_btn.setToolTip("Exports with #!AUTHMATRIX shebang and behavior logic")
        authmatrix_btn.clicked.connect(self._export_authmatrix)
        layout.addWidget(authmatrix_btn)
        
        postman_btn = QtWidgets.QPushButton("Export as Postman Collection")
        postman_btn.setToolTip("Exports as standard Postman collection JSON")
        postman_btn.clicked.connect(self._export_postman)
        layout.addWidget(postman_btn)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
    
    def _export_authmatrix(self):
        content = self.store.export_as_authmatrix()
        show_text(self.parent(), "AuthMatrix Export", content)
        self.accept()
    
    def _export_postman(self):
        content = self.store.export_as_postman()
        show_text(self.parent(), "Postman Collection Export", content)
        self.accept()


class ImportDialog(QtWidgets.QDialog):
    """Dialog for importing AuthMatrix specs or multiple Postman collections"""
    
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Import API Specification")
        self.setModal(True)
        self.resize(640, 480)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Import type selection
        type_group = QtWidgets.QGroupBox("Import Type")
        type_layout = QtWidgets.QVBoxLayout(type_group)
        
        self.authmatrix_radio = QtWidgets.QRadioButton("AuthMatrix Format")
        self.authmatrix_radio.setToolTip("Import a single AuthMatrix specification file with #!AUTHMATRIX shebang")
        self.authmatrix_radio.setChecked(True)
        
        self.single_postman_radio = QtWidgets.QRadioButton("Single Postman Collection")
        self.single_postman_radio.setToolTip("Import one Postman collection and configure authorization manually")
        
        self.multi_postman_radio = QtWidgets.QRadioButton("Multiple Postman Collections")
        self.multi_postman_radio.setToolTip("Import multiple Postman collections to automatically infer authorization patterns")
        
        type_layout.addWidget(self.authmatrix_radio)
        type_layout.addWidget(self.single_postman_radio)
        type_layout.addWidget(self.multi_postman_radio)
        
        layout.addWidget(type_group)
        
        # Content area that changes based on selection
        self.content_stack = QtWidgets.QStackedWidget()
        
        # AuthMatrix import page
        authmatrix_page = self._create_authmatrix_import_page()
        self.content_stack.addWidget(authmatrix_page)
        
        # Single Postman import page
        single_postman_page = self._create_single_postman_import_page()
        self.content_stack.addWidget(single_postman_page)
        
        # Multi Postman import page
        multi_postman_page = self._create_multi_postman_import_page()
        self.content_stack.addWidget(multi_postman_page)
        
        layout.addWidget(self.content_stack)
        
        # Connect radio buttons
        self.authmatrix_radio.toggled.connect(lambda checked: self.content_stack.setCurrentIndex(0) if checked else None)
        self.single_postman_radio.toggled.connect(lambda checked: self.content_stack.setCurrentIndex(1) if checked else None)
        self.multi_postman_radio.toggled.connect(lambda checked: self.content_stack.setCurrentIndex(2) if checked else None)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        import_btn = QtWidgets.QPushButton("Import")
        import_btn.clicked.connect(self._handle_import)
        button_layout.addWidget(import_btn)
        
        layout.addLayout(button_layout)
        
        # Store for multi-collection import
        self.imported_collections = {}
    
    def _create_authmatrix_import_page(self):
        """Create the AuthMatrix import page"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        info_label = QtWidgets.QLabel(
            "Import an AuthMatrix specification file.\n"
            "AuthMatrix files start with #!AUTHMATRIX and contain complete auth testing configuration."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.authmatrix_text = QtWidgets.QTextEdit()
        self.authmatrix_text.setPlaceholderText("Paste AuthMatrix JSON content here...")
        layout.addWidget(self.authmatrix_text)
        
        return page
    
    def _create_single_postman_import_page(self):
        """Create the single Postman collection import page"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        info_label = QtWidgets.QLabel(
            "Import a single Postman collection.\n"
            "You'll be able to configure authorization roles and behavior after import."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.single_postman_text = QtWidgets.QTextEdit()
        self.single_postman_text.setPlaceholderText("Paste Postman collection JSON content here...")
        layout.addWidget(self.single_postman_text)
        
        return page
    
    def _create_multi_postman_import_page(self):
        """Create the multiple Postman collections import page"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        
        info_label = QtWidgets.QLabel(
            "Import multiple Postman collections to automatically configure authorization patterns.\n\n"
            "Example workflow:\n"
            "• Import 'Admin.postman_collection.json' with admin endpoints\n"
            "• Import 'User.postman_collection.json' with user endpoints\n"
            "• Import 'Public.postman_collection.json' with public endpoints\n\n"
            "The tool will automatically determine which roles can access which endpoints based on which collections they appear in."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Collections management
        collections_group = QtWidgets.QGroupBox("Imported Collections")
        collections_layout = QtWidgets.QVBoxLayout(collections_group)
        
        # Add collection buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        add_file_btn = QtWidgets.QPushButton("Add Collection File")
        add_file_btn.clicked.connect(self._add_collection_file)
        btn_layout.addWidget(add_file_btn)
        
        add_text_btn = QtWidgets.QPushButton("Add Collection Text")
        add_text_btn.clicked.connect(self._add_collection_text)
        btn_layout.addWidget(add_text_btn)
        
        clear_btn = QtWidgets.QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_collections)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        collections_layout.addLayout(btn_layout)
        
        # Collections list
        self.collections_list = QtWidgets.QListWidget()
        collections_layout.addWidget(self.collections_list)
        
        # Analysis preview
        self.analysis_text = QtWidgets.QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMaximumHeight(150)
        self.analysis_text.setPlaceholderText("Authorization pattern analysis will appear here...")
        collections_layout.addWidget(QtWidgets.QLabel("Authorization Pattern Preview:"))
        collections_layout.addWidget(self.analysis_text)
        
        layout.addWidget(collections_group)
        
        return page
    
    def _add_collection_file(self):
        """Add a collection from file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Postman Collection", 
            "", "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
            
            self._process_collection_data(collection_data, file_path)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Import Error", 
                f"Failed to load collection file:\n{str(e)}"
            )
    
    def _add_collection_text(self):
        """Add a collection from pasted text"""
        text, ok = multiline_input(self, "Add Postman Collection", "Paste Postman collection JSON:")
        if not ok or not text.strip():
            return
        
        try:
            import json
            collection_data = json.loads(text)
            self._process_collection_data(collection_data, "pasted_content")
            
        except json.JSONDecodeError as e:
            QtWidgets.QMessageBox.critical(
                self, "Import Error", 
                f"Invalid JSON format:\n{str(e)}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Import Error", 
                f"Failed to process collection:\n{str(e)}"
            )
    
    def _process_collection_data(self, collection_data, source_path):
        """Process and add a collection to the import list"""
        # Extract collection info
        collection_name = collection_data.get("info", {}).get("name", "Unknown Collection")
        
        # Parse collection first to get auth config
        endpoints, auth_config = self._parse_postman_collection(collection_data)
        
        if not endpoints:
            QtWidgets.QMessageBox.warning(
                self, "No Endpoints Found", 
                f"No valid endpoints found in collection '{collection_name}'"
            )
            return
        
        # Let user specify the role name and modify auth config
        dialog = RoleAuthConfigDialog(
            self, 
            collection_name, 
            self._suggest_role_name(collection_name),
            auth_config
        )
        
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        
        role_name, updated_auth_config = dialog.get_config()
        
        # Store collection data
        self.imported_collections[role_name] = {
            "collection_name": collection_name,
            "source_path": source_path,
            "endpoints": endpoints,
            "auth_config": updated_auth_config,
            "collection_data": collection_data
        }
        
        # Update UI
        self._update_collections_display()
    
    def _suggest_role_name(self, collection_name):
        """Suggest a role name based on collection name"""
        name_lower = collection_name.lower()
        if "admin" in name_lower:
            return "admin"
        elif "user" in name_lower:
            return "user"
        elif "guest" in name_lower or "public" in name_lower:
            return "guest"
        elif "moderator" in name_lower or "mod" in name_lower:
            return "moderator"
        else:
            # Use first word or full name
            words = collection_name.split()
            return words[0].lower() if words else "role"
    
    def _parse_postman_collection(self, collection_data):
        """Parse Postman collection to extract endpoints and auth config"""
        endpoints = []
        auth_config = {}
        
        # Extract auth from collection level
        collection_auth = collection_data.get("auth", {})
        if collection_auth:
            auth_config = self._extract_auth_config(collection_auth)
        
        # Recursively extract requests
        def extract_requests(items, folder_path=""):
            for item in items:
                if "request" in item:
                    # This is a request
                    request = item["request"]
                    method = request.get("method", "GET")
                    
                    # Extract URL path
                    url_data = request.get("url", {})
                    path = "/"
                    
                    if isinstance(url_data, str):
                        path = self._extract_path_from_url(url_data)
                    elif isinstance(url_data, dict):
                        if "path" in url_data:
                            path_segments = url_data["path"]
                            if isinstance(path_segments, list):
                                path = "/" + "/".join(str(seg) for seg in path_segments if seg)
                        elif "raw" in url_data:
                            path = self._extract_path_from_url(url_data["raw"])
                    
                    # Ensure path starts with /
                    if not path.startswith("/"):
                        path = "/" + path
                    
                    endpoints.append({
                        "name": item.get("name", f"{method} {path}"),
                        "method": method,
                        "path": path,
                        "folder": folder_path
                    })
                
                elif "item" in item:
                    # This is a folder
                    folder_name = item.get("name", "")
                    new_folder_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                    extract_requests(item["item"], new_folder_path)
        
        # Extract from collection items
        if "item" in collection_data:
            extract_requests(collection_data["item"])
        
        return endpoints, auth_config
    
    def _extract_path_from_url(self, url_string):
        """Extract path from a URL string"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url_string)
            path = parsed.path or "/"
            # Remove query parameters
            if "?" in path:
                path = path.split("?")[0]
            return path
        except:
            return "/"
    
    def _extract_auth_config(self, auth_data):
        """Extract authentication configuration from Postman auth"""
        auth_config = {"type": "none"}
        
        auth_type = auth_data.get("type", "")
        
        if auth_type == "bearer":
            bearer_data = auth_data.get("bearer", [])
            token = ""
            for item in bearer_data:
                if item.get("key") == "token":
                    token = item.get("value", "")
                    break
            auth_config = {"type": "bearer", "token": token}
        
        return auth_config
    
    def _update_collections_display(self):
        """Update collections list and analysis"""
        self.collections_list.clear()
        
        for role_name, data in self.imported_collections.items():
            collection_name = data["collection_name"]
            endpoint_count = len(data["endpoints"])
            auth_type = data["auth_config"].get("type", "none")
            
            item_text = f"{role_name}: {collection_name} ({endpoint_count} endpoints, auth: {auth_type})"
            self.collections_list.addItem(item_text)
        
        # Update analysis
        self._update_analysis()
    
    def _update_analysis(self):
        """Update the authorization pattern analysis"""
        if not self.imported_collections:
            self.analysis_text.clear()
            return
        
        # Analyze endpoint access patterns
        endpoint_access = {}  # {endpoint_path: set(roles)}
        
        for role_name, data in self.imported_collections.items():
            for endpoint in data["endpoints"]:
                path = endpoint["path"]
                if path not in endpoint_access:
                    endpoint_access[path] = set()
                endpoint_access[path].add(role_name)
        
        # Generate analysis text
        analysis_lines = []
        analysis_lines.append("=== AUTHORIZATION PATTERN ANALYSIS ===\n")
        
        # Show role summary
        analysis_lines.append("Roles found:")
        for role_name, data in self.imported_collections.items():
            endpoint_count = len(data["endpoints"])
            auth_type = data["auth_config"].get("type", "none")
            analysis_lines.append(f"  • {role_name}: {endpoint_count} endpoints (auth: {auth_type})")
        
        analysis_lines.append("")
        
        # Show access patterns
        analysis_lines.append("Access patterns that will be configured:")
        
        # Group by access pattern
        access_patterns = {}  # {frozenset(roles): [endpoints]}
        for endpoint, roles in endpoint_access.items():
            role_key = frozenset(roles)
            if role_key not in access_patterns:
                access_patterns[role_key] = []
            access_patterns[role_key].append(endpoint)
        
        for roles, endpoints in access_patterns.items():
            roles_list = sorted(list(roles))
            analysis_lines.append(f"  • Accessible to {', '.join(roles_list)}:")
            for endpoint in sorted(endpoints):
                analysis_lines.append(f"    - {endpoint}")
        
        # Show what will happen with guest role
        analysis_lines.append("")
        analysis_lines.append("Additional configuration:")
        analysis_lines.append("  • 'guest' role will be added for unauthorized access testing")
        analysis_lines.append("  • All endpoints will return 403 for guest role by default")
        analysis_lines.append("  • Roles with bearer tokens will get 200 for their endpoints")
        analysis_lines.append("  • Roles without bearer tokens will get 403 for restricted endpoints")
        
        self.analysis_text.setPlainText("\n".join(analysis_lines))
    
    def _clear_collections(self):
        """Clear all imported collections"""
        self.imported_collections.clear()
        self._update_collections_display()
    
    def _handle_import(self):
        """Handle the import based on selected type"""
        if self.authmatrix_radio.isChecked():
            self._import_authmatrix()
        elif self.single_postman_radio.isChecked():
            self._import_single_postman()
        elif self.multi_postman_radio.isChecked():
            self._import_multi_postman()
    
    def _import_authmatrix(self):
        """Import AuthMatrix format"""
        content = self.authmatrix_text.toPlainText().strip()
        if not content:
            QtWidgets.QMessageBox.warning(self, "No Content", "Please paste AuthMatrix content to import.")
            return
        
        if self.store.load_spec_from_content(content):
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Import Error", "Invalid AuthMatrix format")
    
    def _import_single_postman(self):
        """Import single Postman collection"""
        content = self.single_postman_text.toPlainText().strip()
        if not content:
            QtWidgets.QMessageBox.warning(self, "No Content", "Please paste Postman collection content to import.")
            return
        
        if self.store.load_spec_from_content(content):
            # Show configuration dialog for single import
            if self.store._original_postman_data and not self._has_configured_expectations():
                dialog = PostmanConfigDialog(self.store, self)
                if dialog.exec() == QtWidgets.QDialog.Accepted:
                    self.accept()
                else:
                    # User cancelled configuration but import was successful
                    self.accept()
            else:
                self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Import Error", "Invalid Postman collection format")
    
    def _import_multi_postman(self):
        """Import multiple Postman collections and auto-configure"""
        if not self.imported_collections:
            QtWidgets.QMessageBox.warning(self, "No Collections", "Please add at least one Postman collection to import.")
            return
        
        # Merge all collections into a single AuthMatrix spec
        merged_spec = self._merge_collections_to_authmatrix()
        
        # Load the merged spec
        import json
        spec_json = json.dumps(merged_spec)
        if self.store.load_spec_from_content(spec_json):
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Import Error", "Failed to process merged collections")
    
    def _merge_collections_to_authmatrix(self):
        """Merge multiple collections into a single AuthMatrix specification"""
        # Start with base spec
        merged_spec = {
            "base_url": "",
            "default_headers": {"Accept": "application/json"},
            "roles": {"guest": {"auth": {"type": "none"}}},
            "endpoints": []
        }
        
        # Extract base URL from first collection
        if self.imported_collections:
            first_collection = next(iter(self.imported_collections.values()))
            merged_spec["base_url"] = self._extract_base_url_from_collection(first_collection["collection_data"])
        
        # Add roles from collections
        for role_name, data in self.imported_collections.items():
            auth_config = data["auth_config"]
            merged_spec["roles"][role_name] = {"auth": auth_config}
        
        # Collect all unique endpoints
        all_endpoints = {}  # {(method, path): {endpoint_data, access_roles}}
        
        for role_name, data in self.imported_collections.items():
            for endpoint in data["endpoints"]:
                key = (endpoint["method"], endpoint["path"])
                if key not in all_endpoints:
                    all_endpoints[key] = {
                        "endpoint": endpoint,
                        "access_roles": set()
                    }
                all_endpoints[key]["access_roles"].add(role_name)
        
        # Create endpoints with expectations
        for (method, path), endpoint_data in all_endpoints.items():
            endpoint = endpoint_data["endpoint"]
            access_roles = endpoint_data["access_roles"]
            
            # Create expectations for all roles
            expectations = {}
            for role_name in merged_spec["roles"]:
                if role_name in access_roles:
                    # This role should have access
                    expectations[role_name] = {"status": 200}
                else:
                    # This role should be denied
                    expectations[role_name] = {"status": 403}
            
            merged_spec["endpoints"].append({
                "name": endpoint["name"],
                "method": endpoint["method"],
                "path": endpoint["path"],
                "expect": expectations
            })
        
        return merged_spec
    
    def _extract_base_url_from_collection(self, collection_data):
        """Extract base URL from a Postman collection"""
        # This reuses the logic from SpecStore
        return self.store.extract_base_url_from_postman(collection_data)
    
    def _has_configured_expectations(self):
        """Check if any endpoints have configured expectations"""
        for endpoint in self.store.spec.get("endpoints", []):
            if endpoint.get("expect"):
                return True
        return False


class RoleAuthConfigDialog(QtWidgets.QDialog):
    """Dialog for configuring role name and authentication details during import"""
    
    def __init__(self, parent, collection_name, suggested_role_name, auth_config):
        super().__init__(parent)
        self.setWindowTitle("Configure Role and Authentication")
        self.setModal(True)
        self.resize(400, 240)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label
        info_label = QtWidgets.QLabel(f"Configure role and authentication for collection:\n'{collection_name}'")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-weight: bold; padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Form layout
        form_layout = QtWidgets.QFormLayout()
        
        # Role name
        self.role_name_edit = QtWidgets.QLineEdit(suggested_role_name)
        self.role_name_edit.setPlaceholderText("e.g., admin, user, guest")
        form_layout.addRow("Role Name:", self.role_name_edit)
        
        # Auth type
        self.auth_type_combo = QtWidgets.QComboBox()
        self.auth_type_combo.addItems(["none", "bearer"])
        auth_type = auth_config.get("type", "none")
        self.auth_type_combo.setCurrentText(auth_type)
        self.auth_type_combo.currentTextChanged.connect(self._on_auth_type_changed)
        form_layout.addRow("Auth Type:", self.auth_type_combo)
        
        # Token field (only shown for bearer auth)
        self.token_edit = QtWidgets.QLineEdit()
        self.token_edit.setPlaceholderText("Enter bearer token...")
        current_token = auth_config.get("token", "")
        self.token_edit.setText(current_token)
        self.token_label = QtWidgets.QLabel("Token:")
        form_layout.addRow(self.token_label, self.token_edit)
        
        layout.addLayout(form_layout)
        
        # Info about token
        token_info = QtWidgets.QLabel(
            "💡 Tip: You can modify the token extracted from the collection or enter a new one. "
            "Leave empty for 'none' auth type."
        )
        token_info.setWordWrap(True)
        token_info.setStyleSheet("color: #666; font-size: 11px; padding: 8px;")
        layout.addWidget(token_info)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self._validate_and_accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Initial state
        self._on_auth_type_changed()
        
        # Focus on role name field
        self.role_name_edit.setFocus()
        self.role_name_edit.selectAll()
    
    def _on_auth_type_changed(self):
        """Show/hide token field based on auth type"""
        auth_type = self.auth_type_combo.currentText()
        is_bearer = auth_type == "bearer"
        
        self.token_label.setVisible(is_bearer)
        self.token_edit.setVisible(is_bearer)
    
    def _validate_and_accept(self):
        """Validate input before accepting"""
        role_name = self.role_name_edit.text().strip()
        if not role_name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Role name is required.")
            self.role_name_edit.setFocus()
            return
        
        auth_type = self.auth_type_combo.currentText()
        if auth_type == "bearer":
            token = self.token_edit.text().strip()
            if not token:
                reply = QtWidgets.QMessageBox.question(
                    self, "Empty Token", 
                    "Bearer token is empty. This will create a role with no authentication.\n\n"
                    "Continue anyway?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if reply != QtWidgets.QMessageBox.Yes:
                    self.token_edit.setFocus()
                    return
        
        self.accept()
    
    def get_config(self):
        """Get the configured role name and auth config"""
        role_name = self.role_name_edit.text().strip().lower()
        auth_type = self.auth_type_combo.currentText()
        
        if auth_type == "bearer":
            token = self.token_edit.text().strip()
            auth_config = {"type": "bearer", "token": token}
        else:
            auth_config = {"type": "none"}
        
        return role_name, auth_config


# ------------------------------
# Public entrypoint
# ------------------------------
def start_ui(runner: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None):
    # Ensure multiprocessing works properly on Windows
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Already set, ignore
        pass
    
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    mw = MainWindow(runner=runner)
    mw.show()
    app.exec()

# demo
if __name__ == "__main__":
    # Set multiprocessing start method for Windows compatibility
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        # Already set, ignore
        pass
    start_ui()
