from PySide6 import QtWidgets, QtGui, QtCore
from .SpecStore import SpecStore
from . import Theme

class EndpointsSection(QtWidgets.QWidget):
    """Editable table for managing API endpoints."""
    def __init__(self, store: SpecStore, parent=None):
        super().__init__(parent)
        self.store = store

        # Button bar
        buttonLayout = QtWidgets.QHBoxLayout()
        addBtn = QtWidgets.QPushButton("Add Endpoint")
        addBtn.clicked.connect(self.add_endpoint)
        buttonLayout.addWidget(addBtn)
        
        configureAllBtn = QtWidgets.QPushButton("Configure All")
        configureAllBtn.setToolTip("Configure auth behavior for all endpoints at once")
        configureAllBtn.clicked.connect(self.configure_all_endpoints)
        buttonLayout.addWidget(configureAllBtn)
        
        buttonLayout.addStretch()

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Name", "Method", "Path", "Behaviours", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # Name - fit content
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)  # Method - fit content  
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)       # Path - user resizable with reasonable default
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)           # Behaviours - take most available space
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)  # Actions - fit content
        
        # Set initial column widths for better proportions
        self.table.setColumnWidth(2, 300)  # Path column - reasonable fixed width
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.table)

        self.store.specChanged.connect(self.refresh)
        self.refresh()

    def add_endpoint(self):
        """Add a new endpoint by opening an empty edit form."""
        self._edit_endpoint_form("", "GET", "", is_new=True)

    def configure_all_endpoints(self):
        """Open a dialog to configure behavior for all endpoints at once."""
        if not self.store.spec.get("endpoints"):
            QtWidgets.QMessageBox.information(
                self, "No Endpoints", 
                "No endpoints found. Please add some endpoints first before configuring behaviors."
            )
            return
        
        dialog = ConfigureAllEndpointsDialog(self.store, self)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            self.refresh()  # Refresh the table to show updated configurations

    def refresh(self):
        eps = self.store.spec.get("endpoints", [])
        self.table.setRowCount(len(eps))
        for i, ep in enumerate(eps):
            # Name
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(ep.get("name","")))
            # Method (combo)
            combo = QtWidgets.QComboBox()
            combo.addItems(["GET","POST","PUT","PATCH","DELETE"])
            combo.setCurrentText(ep.get("method","GET"))
            combo.wheelEvent = lambda event: None  # Disable mouse wheel scrolling
            combo.currentTextChanged.connect(lambda m, row=i: self._on_method_change(row, m))
            self.table.setCellWidget(i, 1, combo)
            # Path (text display with truncation and tooltip)
            full_path = ep.get("path", "")
            display_path = full_path
            
            # Truncate URL if longer than 40 characters (more generous since Path column stretches)
            if len(full_path) > 40:
                display_path = full_path[:37] + "..."
            
            path_item = QtWidgets.QTableWidgetItem(display_path)
            path_item.setForeground(QtGui.QColor(Theme.secondary))
            
            # Add tooltip with full path if truncated
            if len(full_path) > 40:
                path_item.setToolTip(full_path)
            
            self.table.setItem(i, 2, path_item)
            # Expectations summary
            expectations = ep.get("expect", {})
            if expectations:
                # Create a detailed summary of configured behaviors
                behavior_summaries = []
                role_behaviors = {}
                
                # Group expectations by behavior to show unique behaviors
                for role_name, exp in expectations.items():
                    behavior_key = self._create_behavior_key(exp)
                    if behavior_key not in role_behaviors:
                        role_behaviors[behavior_key] = {"behavior": exp, "roles": []}
                    role_behaviors[behavior_key]["roles"].append(role_name)
                
                # Create summary text for each unique behavior
                for behavior_data in role_behaviors.values():
                    behavior = behavior_data["behavior"]
                    roles = behavior_data["roles"]
                    
                    # Build behavior description
                    desc_parts = []
                    if "status" in behavior:
                        status_val = behavior["status"]
                        if isinstance(status_val, list):
                            desc_parts.append(f"Status {','.join(map(str, status_val))}")
                        else:
                            desc_parts.append(f"Status {status_val}")
                    if "contains" in behavior:
                        desc_parts.append(f"Contains {','.join(behavior['contains'])}")
                    if "not_contains" in behavior:
                        desc_parts.append(f"Not Contains {','.join(behavior['not_contains'])}")
                    
                    behavior_desc = " | ".join(desc_parts) if desc_parts else "No criteria"
                    roles_desc = f"[{', '.join(roles)}]"
                    
                    behavior_summaries.append(f"{behavior_desc} {roles_desc}")
                
                # Join all behaviors and truncate if needed
                full_summary = " • ".join(behavior_summaries)
                
                # Create label with tooltip for full content
                exp_label = QtWidgets.QLabel(full_summary)
                exp_label.setWordWrap(True)
                exp_label.setToolTip(full_summary)  # Show full content on hover
                exp_label.setStyleSheet("QLabel { padding: 4px; }")
            else:
                exp_label = QtWidgets.QLabel("Not configured")
                exp_label.setStyleSheet("QLabel { padding: 4px; color: #999; font-style: italic; }")
            
            self.table.setCellWidget(i, 3, exp_label)
            # Actions
            actionsWidget = QtWidgets.QWidget()
            actionsLayout = QtWidgets.QHBoxLayout(actionsWidget)
            actionsLayout.setContentsMargins(2, 2, 2, 2)
            
            editBtn = QtWidgets.QPushButton("Edit")
            editBtn.clicked.connect(lambda _=None, row=i: self._edit_endpoint_row(row))
            deleteBtn = QtWidgets.QPushButton("Delete")
            deleteBtn.clicked.connect(lambda _=None, row=i: self._delete_endpoint(row))
            
            actionsLayout.addWidget(editBtn)
            actionsLayout.addWidget(deleteBtn)
            actionsLayout.addStretch()
            
            self.table.setCellWidget(i, 4, actionsWidget)

    def _on_method_change(self, row: int, method: str):
        ep = self.store.spec["endpoints"][row]
        self.store.update_endpoint_row(row, ep.get("name",""), method, ep.get("path",""))

    def _delete_endpoint(self, row: int):
        """Delete an endpoint after confirmation."""
        ep = self.store.spec["endpoints"][row]
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete endpoint '{ep.get('name', '')}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.store.delete_endpoint(row)

    def _edit_endpoint_row(self, row: int):
        """Edit an existing endpoint."""
        ep = self.store.spec["endpoints"][row]
        name, method, path = ep.get("name",""), ep.get("method","GET"), ep.get("path","")
        self._edit_endpoint_form(name, method, path, is_new=False, row=row)

    def _edit_endpoint_form(self, name: str, method: str, path: str, is_new: bool = False, row: int = -1):
        """Show endpoint edit form for new or existing endpoints."""
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Add Endpoint" if is_new else "Edit Endpoint")
        dlg.setModal(True)
        dlg.resize(600, 700)
        
        layout = QtWidgets.QVBoxLayout(dlg)
        
        # Basic endpoint info - compact form at top
        basicGroup = QtWidgets.QGroupBox("Endpoint Details")
        basicForm = QtWidgets.QFormLayout(basicGroup)
        
        nameEdit = QtWidgets.QLineEdit(name)
        nameEdit.setPlaceholderText("e.g., Get Users, Login, Update Profile")
        
        methodCombo = QtWidgets.QComboBox()
        methodCombo.addItems(["GET","POST","PUT","PATCH","DELETE"])
        methodCombo.setCurrentText(method)
        methodCombo.wheelEvent = lambda event: None  # Disable mouse wheel scrolling
        
        pathEdit = QtWidgets.QLineEdit(path)
        pathEdit.setPlaceholderText("e.g., /api/users, /login, /profile")
        
        basicForm.addRow("Name:", nameEdit)
        basicForm.addRow("Method:", methodCombo)
        basicForm.addRow("Path:", pathEdit)
        
        layout.addWidget(basicGroup)
        
        # Behaviors list area - uses the rest of the space
        behaviorsGroup = QtWidgets.QGroupBox("Behaviors")
        behaviorsLayout = QtWidgets.QVBoxLayout(behaviorsGroup)
        
        # Scroll area for behaviors
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollWidget = QtWidgets.QWidget()
        behaviorsList = QtWidgets.QVBoxLayout(scrollWidget)
        behaviorsList.addStretch()  # Push behaviors to top
        scrollArea.setWidget(scrollWidget)
        
        behaviorsLayout.addWidget(scrollArea)
        
        # Add Behavior button - always at bottom of behaviors section
        addBehaviorBtn = QtWidgets.QPushButton("+ Add Behavior")
        addBehaviorBtn.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        behaviorsLayout.addWidget(addBehaviorBtn)
        
        layout.addWidget(behaviorsGroup)
        
        # Hidden behavior editing panel
        behaviorEditWidget = QtWidgets.QWidget()
        behaviorEditLayout = QtWidgets.QVBoxLayout(behaviorEditWidget)
        behaviorEditWidget.setVisible(False)
        
        behaviorEditGroup = QtWidgets.QGroupBox("Edit Behavior")
        behaviorEditForm = QtWidgets.QFormLayout(behaviorEditGroup)
        
        statusEdit = QtWidgets.QLineEdit()
        statusEdit.setPlaceholderText("e.g., 200 or 200,204")
        
        containsEdit = QtWidgets.QLineEdit()
        containsEdit.setPlaceholderText("Body must contain (comma-separated)")
        
        notContainsEdit = QtWidgets.QLineEdit()
        notContainsEdit.setPlaceholderText("Body must NOT contain (comma-separated)")
        
        # Role assignment dropdown
        roleCombo = QtWidgets.QComboBox()
        roleCombo.setEditable(False)
        
        behaviorEditForm.addRow("Expected Status:", statusEdit)
        behaviorEditForm.addRow("Must Contain:", containsEdit)
        behaviorEditForm.addRow("Must NOT Contain:", notContainsEdit)
        behaviorEditForm.addRow("Assign to Roles:", roleCombo)
        
        # Behavior edit buttons
        behaviorBtnLayout = QtWidgets.QHBoxLayout()
        saveBehaviorBtn = QtWidgets.QPushButton("Save Behavior")
        cancelBehaviorBtn = QtWidgets.QPushButton("Cancel")
        behaviorBtnLayout.addWidget(saveBehaviorBtn)
        behaviorBtnLayout.addWidget(cancelBehaviorBtn)
        behaviorEditForm.addRow(behaviorBtnLayout)
        
        behaviorEditLayout.addWidget(behaviorEditGroup)
        layout.addWidget(behaviorEditWidget)
        
        # Store behaviors data
        behaviors_data = []
        current_edit_index = -1  # -1 for new behavior, >= 0 for editing existing
        
        # Get current expectations if editing
        if not is_new and 0 <= row < len(self.store.spec["endpoints"]):
            current_expectations = self.store.spec["endpoints"][row].get("expect", {})
            # Convert current expectations to behaviors format
            role_to_behavior = {}
            for role_name, exp in current_expectations.items():
                behavior_key = self._create_behavior_key(exp)
                if behavior_key not in role_to_behavior:
                    role_to_behavior[behavior_key] = {"behavior": exp, "roles": []}
                role_to_behavior[behavior_key]["roles"].append(role_name)
            
            behaviors_data = list(role_to_behavior.values())
        
        def update_role_combo():
            roleCombo.clear()
            available_roles = list(self.store.spec.get("roles", {}).keys())
            if not available_roles:
                roleCombo.addItem("No roles available")
                roleCombo.setEnabled(False)
            else:
                # Add multi-select options
                roleCombo.addItem("Select roles...")
                for role in available_roles:
                    roleCombo.addItem(role)
                roleCombo.setEnabled(True)
        
        def create_behavior_item(behavior_data, index):
            itemWidget = QtWidgets.QWidget()
            itemWidget.setStyleSheet("""
                QWidget {
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    padding: 8px;
                    margin: 2px;
                    background-color: #f8f9fa;
                }
                QWidget:hover {
                    background-color: #e9ecef;
                    border-color: #007bff;
                }
            """)
            itemLayout = QtWidgets.QHBoxLayout(itemWidget)
            itemLayout.setContentsMargins(8, 4, 8, 4)
            
            # Behavior description bubble
            behavior = behavior_data["behavior"]
            desc_parts = []
            if "status" in behavior:
                status_val = behavior["status"]
                if isinstance(status_val, list):
                    desc_parts.append(f"Status {','.join(map(str, status_val))}")
                else:
                    desc_parts.append(f"Status {status_val}")
            if "contains" in behavior:
                desc_parts.append(f"Contains {','.join(behavior['contains'])}")
            if "not_contains" in behavior:
                desc_parts.append(f"Not Contains {','.join(behavior['not_contains'])}")
            
            description = " | ".join(desc_parts) if desc_parts else "No criteria"
            
            # Truncate behavior description if too long
            max_behavior_width = 300  # pixels
            char_width = 8  # approximate character width
            max_chars = max_behavior_width // char_width
            
            if len(description) > max_chars:
                description = description[:max_chars-3] + "..."
            
            descLabel = QtWidgets.QLabel(description)
            descLabel.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-weight: bold;
                    color: #1976d2;
                }
            """)
            descLabel.setMaximumWidth(320)
            descLabel.setToolTip(" | ".join(desc_parts) if desc_parts else "No criteria")  # Show full description on hover
            itemLayout.addWidget(descLabel)
            
            # Roles bubble - no stretch before it, so it stays close to behavior
            if behavior_data["roles"]:
                roles_list = behavior_data["roles"]
                # Calculate approximate space available for roles (rough estimate)
                max_roles_width = 200  # pixels
                char_width = 8  # approximate character width
                max_chars = max_roles_width // char_width
                
                roles_text = ", ".join(roles_list)
                if len(roles_text) > max_chars:
                    # Truncate and add ellipsis
                    truncated = ""
                    for role in roles_list:
                        test_text = f"{truncated}, {role}" if truncated else role
                        if len(test_text) > max_chars - 3:  # Reserve space for "..."
                            if truncated:
                                roles_text = f"{truncated}..."
                            else:
                                roles_text = f"{role[:max_chars-3]}..."
                            break
                        truncated = test_text
                    else:
                        roles_text = truncated
                
                rolesLabel = QtWidgets.QLabel(f"[{roles_text}]")
                rolesLabel.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e8;
                        padding: 4px 8px;
                        border-radius: 12px;
                        color: #2e7d32;
                        font-weight: 500;
                        margin-left: 12px;
                    }
                """)
                rolesLabel.setMaximumWidth(220)
                rolesLabel.setToolTip(f"Roles: {', '.join(roles_list)}")  # Show full list on hover
            else:
                rolesLabel = QtWidgets.QLabel("[no roles]")
                rolesLabel.setStyleSheet("""
                    QLabel {
                        background-color: #ffebee;
                        padding: 4px 8px;
                        border-radius: 12px;
                        color: #c62828;
                        font-style: italic;
                        margin-left: 12px;
                    }
                """)
            
            itemLayout.addWidget(rolesLabel)
            
            # Add stretch AFTER roles to push buttons to the right
            itemLayout.addStretch()
            
            # Buttons
            editBtn = QtWidgets.QPushButton("Edit")
            editBtn.setStyleSheet("QPushButton { background-color: #007bff; color: white; border: none; padding: 4px 12px; border-radius: 3px; margin-left: 8px; }")
            deleteBtn = QtWidgets.QPushButton("Delete")
            deleteBtn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; padding: 4px 12px; border-radius: 3px; margin-left: 4px; }")
            
            editBtn.clicked.connect(lambda: edit_behavior(index))
            deleteBtn.clicked.connect(lambda: delete_behavior(index))
            
            itemLayout.addWidget(editBtn)
            itemLayout.addWidget(deleteBtn)
            
            return itemWidget
        
        def show_behavior_edit(edit_index=-1):
            nonlocal current_edit_index
            current_edit_index = edit_index
            
            # Clear form
            statusEdit.clear()
            containsEdit.clear()
            notContainsEdit.clear()
            
            if edit_index >= 0 and edit_index < len(behaviors_data):
                # Editing existing behavior
                behavior = behaviors_data[edit_index]["behavior"]
                behaviorEditGroup.setTitle("Edit Behavior")
                
                # Load values
                if "status" in behavior:
                    status_val = behavior["status"]
                    if isinstance(status_val, list):
                        statusEdit.setText(",".join(map(str, status_val)))
                    else:
                        statusEdit.setText(str(status_val))
                
                if "contains" in behavior:
                    containsEdit.setText(",".join(behavior["contains"]))
                
                if "not_contains" in behavior:
                    notContainsEdit.setText(",".join(behavior["not_contains"]))
            else:
                # New behavior
                behaviorEditGroup.setTitle("Add New Behavior")
            
            update_role_combo()
            behaviorEditWidget.setVisible(True)
            addBehaviorBtn.setVisible(False)
        
        def hide_behavior_edit():
            behaviorEditWidget.setVisible(False)
            addBehaviorBtn.setVisible(True)
        
        def edit_behavior(index):
            show_behavior_edit(index)
        
        def delete_behavior(index):
            if 0 <= index < len(behaviors_data):
                behaviors_data.pop(index)
                refresh_behaviors_list()
        
        def save_behavior():
            status_text = statusEdit.text().strip()
            contains_text = containsEdit.text().strip()
            not_contains_text = notContainsEdit.text().strip()
            
            # Validate that at least one criteria is specified
            if not any([status_text, contains_text, not_contains_text]):
                QtWidgets.QMessageBox.warning(dlg, "No Criteria", "Please specify at least one expectation criteria.")
                # Focus on the first empty field to help user
                if not status_text:
                    statusEdit.setFocus()
                elif not contains_text:
                    containsEdit.setFocus()
                else:
                    notContainsEdit.setFocus()
                return  # Keep dialog open with user input preserved
            
            behavior = {}
            
            # Parse status
            if status_text:
                try:
                    parts = [int(p.strip()) for p in status_text.split(",") if p.strip()]
                    if len(parts) == 1:
                        behavior["status"] = parts[0]
                    elif len(parts) > 1:
                        behavior["status"] = parts
                except ValueError:
                    QtWidgets.QMessageBox.warning(dlg, "Invalid Status", f"Invalid status code: {status_text}\n\nPlease enter valid HTTP status codes (e.g., 200 or 200,204).")
                    statusEdit.setFocus()
                    statusEdit.selectAll()  # Select the invalid text for easy correction
                    return  # Keep dialog open with user input preserved
            
            # Parse contains
            if contains_text:
                contains_list = [s.strip() for s in contains_text.split(",") if s.strip()]
                if contains_list:
                    behavior["contains"] = contains_list
            
            # Parse not_contains
            if not_contains_text:
                not_contains_list = [s.strip() for s in not_contains_text.split(",") if s.strip()]
                if not_contains_list:
                    behavior["not_contains"] = not_contains_list
            
            # Get selected roles - for now just get the selected role
            # TODO: Implement multi-select role assignment
            selected_roles = []
            if roleCombo.currentIndex() > 0:  # Skip "Select roles..." option
                selected_roles = [roleCombo.currentText()]
            
            if current_edit_index >= 0:
                # Update existing behavior
                behaviors_data[current_edit_index] = {"behavior": behavior, "roles": selected_roles}
            else:
                # Add new behavior
                behaviors_data.append({"behavior": behavior, "roles": selected_roles})
            
            hide_behavior_edit()
            refresh_behaviors_list()
        
        def refresh_behaviors_list():
            # Clear existing items
            for i in reversed(range(behaviorsList.count() - 1)):  # Keep the stretch at the end
                child = behaviorsList.takeAt(i)
                if child.widget():
                    child.widget().deleteLater()
            
            # Add current behaviors
            for i, behavior_data in enumerate(behaviors_data):
                item_widget = create_behavior_item(behavior_data, i)
                behaviorsList.insertWidget(i, item_widget)
        
        # Connect signals
        addBehaviorBtn.clicked.connect(lambda: show_behavior_edit(-1))
        saveBehaviorBtn.clicked.connect(save_behavior)
        cancelBehaviorBtn.clicked.connect(hide_behavior_edit)
        
        # Initialize
        update_role_combo()
        refresh_behaviors_list()
        
        # Button box
        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        layout.addWidget(btns)
        
        def validate_and_accept():
            """Validate form before accepting dialog."""
            endpoint_name = nameEdit.text().strip()
            endpoint_path = pathEdit.text().strip()
            
            # Basic validation - show warnings but keep dialog open
            if not endpoint_name:
                QtWidgets.QMessageBox.warning(dlg, "Validation Error", "Endpoint name is required.\n\nPlease enter a descriptive name for this endpoint (e.g., 'Get Users', 'Login', 'Update Profile').")
                nameEdit.setFocus()
                return
            if not endpoint_path:
                QtWidgets.QMessageBox.warning(dlg, "Validation Error", "Endpoint path is required.\n\nPlease enter the API path for this endpoint (e.g., '/api/users', '/login', '/profile').")
                pathEdit.setFocus()
                return
            
            # If validation passes, accept the dialog
            dlg.accept()
        
        btns.accepted.connect(validate_and_accept)
        btns.rejected.connect(dlg.reject)
        
        # Focus on name field for new endpoints, path for existing
        if is_new:
            nameEdit.setFocus()
        else:
            pathEdit.setFocus()
            pathEdit.selectAll()
        
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            endpoint_name = nameEdit.text().strip()
            endpoint_method = methodCombo.currentText()
            endpoint_path = pathEdit.text().strip()
            
            # Ensure path starts with /
            if not endpoint_path.startswith('/'):
                endpoint_path = '/' + endpoint_path
            
            # Convert behaviors to expectations format
            expectations_data = {}
            for behavior_data in behaviors_data:
                behavior = behavior_data["behavior"]
                for role in behavior_data["roles"]:
                    expectations_data[role] = behavior.copy()
            
            if is_new:
                # Create new endpoint with expectations
                endpoint = {
                    "name": endpoint_name,
                    "method": endpoint_method, 
                    "path": endpoint_path,
                    "expect": expectations_data
                }
                self.store.spec["endpoints"].append(endpoint)
                self.store.specChanged.emit()
            else:
                # Update existing endpoint
                self.store.update_endpoint_row(row, endpoint_name, endpoint_method, endpoint_path)
                # Update expectations
                if 0 <= row < len(self.store.spec["endpoints"]):
                    self.store.spec["endpoints"][row]["expect"] = expectations_data
                    self.store.specChanged.emit()

    def _create_behavior_key(self, behavior):
        """Create a unique key for a behavior to group similar ones."""
        status_key = str(behavior.get("status", ""))
        contains_key = ",".join(sorted(behavior.get("contains", [])))
        not_contains_key = ",".join(sorted(behavior.get("not_contains", [])))
        return f"{status_key}|{contains_key}|{not_contains_key}"


class ConfigureAllEndpointsDialog(QtWidgets.QDialog):
    """Dialog for configuring auth behavior for all endpoints at once"""
    
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Configure All Endpoints")
        self.setModal(True)
        self.resize(900, 700)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label
        info_label = QtWidgets.QLabel(
            "Configure authorization behavior for all endpoints at once.\n"
            "Set up expected responses for different auth levels across your entire API."
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
        self.endpoints_table.setColumnCount(4)
        self.endpoints_table.setHorizontalHeaderLabels(["Endpoint", "Method", "Path", "Configure"])
        self._refresh_endpoints_table()
        endpoints_layout.addWidget(self.endpoints_table)
        
        layout.addWidget(endpoints_group)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        auto_config_btn = QtWidgets.QPushButton("Auto-Configure Common Patterns")
        auto_config_btn.clicked.connect(self._auto_configure)
        button_layout.addWidget(auto_config_btn)
        
        clear_all_btn = QtWidgets.QPushButton("Clear All Configurations")
        clear_all_btn.clicked.connect(self._clear_all_configurations)
        button_layout.addWidget(clear_all_btn)
        
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
            
            # Path
            path_item = QtWidgets.QTableWidgetItem(endpoint.get("path", ""))
            path_item.setFlags(path_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.endpoints_table.setItem(i, 2, path_item)
            
            # Configure button
            config_btn = QtWidgets.QPushButton("Configure")
            config_btn.clicked.connect(lambda checked, idx=i: self._configure_endpoint(idx))
            self.endpoints_table.setCellWidget(i, 3, config_btn)
        
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
        self._refresh_endpoints_table()  # Refresh to show any changes
    
    def _auto_configure(self):
        """Auto-configure common auth patterns"""
        reply = QtWidgets.QMessageBox.question(
            self, "Auto-Configure", 
            "This will set up common patterns:\n"
            "• Public endpoints (/, /health, /status) → 200 for all roles\n"
            "• Admin endpoints (/admin/*) → 403 for guest, 200 for admin\n"
            "• User endpoints (/user/*, /profile) → 403 for guest, 200 for authenticated roles\n"
            "• Other endpoints → 200 for admin, 403 for others\n\n"
            "Continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self._apply_auto_configuration()
    
    def _apply_auto_configuration(self):
        """Apply automatic configuration patterns"""
        public_patterns = ["/", "/health", "/status", "/info", "/version", "/docs"]
        admin_patterns = ["/admin"]
        user_patterns = ["/user", "/profile", "/settings", "/account"]
        
        configured_count = 0
        
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
                configured_count += 1
        
        QtWidgets.QMessageBox.information(
            self, "Auto-Configuration Complete", 
            f"Applied automatic configuration to {len(self.store.spec.get('endpoints', []))} endpoints "
            f"with {configured_count} total role configurations."
        )
    
    def _clear_all_configurations(self):
        """Clear all endpoint configurations"""
        reply = QtWidgets.QMessageBox.question(
            self, "Clear All Configurations", 
            "This will remove all behavior configurations from all endpoints.\n\n"
            "Are you sure you want to continue?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            for endpoint in self.store.spec.get("endpoints", []):
                endpoint["expect"] = {}
            self.store.specChanged.emit()
            QtWidgets.QMessageBox.information(
                self, "Configurations Cleared", 
                "All endpoint behavior configurations have been cleared."
            )


class AddRoleDialog(QtWidgets.QDialog):
    """Dialog for adding a new role"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Role")
        self.setModal(True)
        
        layout = QtWidgets.QFormLayout(self)
        
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("e.g., admin, user, moderator")
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
        ok_btn.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(ok_btn)
        
        layout.addRow(button_layout)
        
        # Focus on name field
        self.name_edit.setFocus()
    
    def _validate_and_accept(self):
        """Validate input before accepting"""
        name = self.name_edit.text().strip()
        if not name:
            QtWidgets.QMessageBox.warning(self, "Validation Error", "Role name is required.")
            self.name_edit.setFocus()
            return
        
        self.accept()
    
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
        self.resize(500, 400)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Endpoint info
        info_label = QtWidgets.QLabel(f"Endpoint: {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
        info_label.setStyleSheet("font-weight: bold; padding: 8px; background-color: #f0f0f0; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Role expectations
        scroll_area = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        self.role_configs = {}
        for role_name in store.spec.get("roles", {}):
            group = QtWidgets.QGroupBox(f"Role: {role_name}")
            group_layout = QtWidgets.QFormLayout(group)
            
            # Status code
            status_edit = QtWidgets.QLineEdit()
            current_expect = endpoint.get("expect", {}).get(role_name, {})
            if "status" in current_expect:
                status_val = current_expect["status"]
                if isinstance(status_val, list):
                    status_edit.setText(",".join(map(str, status_val)))
                else:
                    status_edit.setText(str(status_val))
            else:
                status_edit.setPlaceholderText("e.g., 200, 403, 200,201")
            
            group_layout.addRow("Expected Status:", status_edit)
            
            # Contains
            contains_edit = QtWidgets.QLineEdit()
            if "contains" in current_expect:
                contains_edit.setText(",".join(current_expect["contains"]))
            else:
                contains_edit.setPlaceholderText("e.g., success, data")
            
            group_layout.addRow("Must Contain:", contains_edit)
            
            # Not contains
            not_contains_edit = QtWidgets.QLineEdit()
            if "not_contains" in current_expect:
                not_contains_edit.setText(",".join(current_expect["not_contains"]))
            else:
                not_contains_edit.setPlaceholderText("e.g., error, failed")
            
            group_layout.addRow("Must NOT Contain:", not_contains_edit)
            
            self.role_configs[role_name] = {
                "status": status_edit,
                "contains": contains_edit,
                "not_contains": not_contains_edit
            }
            scroll_layout.addWidget(group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        clear_btn = QtWidgets.QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QtWidgets.QPushButton("Save")
        ok_btn.clicked.connect(self._save_config)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _clear_all(self):
        """Clear all configurations for this endpoint"""
        for widgets in self.role_configs.values():
            widgets["status"].clear()
            widgets["contains"].clear()
            widgets["not_contains"].clear()
    
    def _save_config(self):
        """Save the configuration for this endpoint"""
        import json
        
        for role_name, widgets in self.role_configs.items():
            status_text = widgets["status"].text().strip()
            contains_text = widgets["contains"].text().strip()
            not_contains_text = widgets["not_contains"].text().strip()
            
            # Remove existing expectation if all fields are empty
            if not any([status_text, contains_text, not_contains_text]):
                self.store.remove_endpoint_expectation(self.endpoint_index, role_name)
                continue
            
            # Parse and set expectations
            expectation = {}
            
            if status_text:
                try:
                    # Try to parse as int first, then as list
                    if "," in status_text:
                        status = [int(s.strip()) for s in status_text.split(",") if s.strip()]
                    else:
                        status = int(status_text)
                    expectation["status"] = status
                except ValueError:
                    QtWidgets.QMessageBox.warning(self, "Invalid Status", f"Invalid status code for {role_name}: {status_text}")
                    return
            
            if contains_text:
                contains_list = [s.strip() for s in contains_text.split(",") if s.strip()]
                if contains_list:
                    expectation["contains"] = contains_list
            
            if not_contains_text:
                not_contains_list = [s.strip() for s in not_contains_text.split(",") if s.strip()]
                if not_contains_list:
                    expectation["not_contains"] = not_contains_list
            
            # Set the expectation
            if expectation:
                success, error = self.store.set_endpoint_expectation(
                    self.endpoint_index, role_name,
                    status=expectation.get("status"),
                    contains=expectation.get("contains"),
                    not_contains=expectation.get("not_contains")
                )
                if not success:
                    QtWidgets.QMessageBox.warning(self, "Save Error", error or "Failed to save configuration")
                    return
        
        self.accept()
