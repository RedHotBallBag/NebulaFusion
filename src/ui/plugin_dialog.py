#!/usr/bin/env python3
# NebulaFusion Browser - Plugin Dialog

import os
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QLabel, QMenu, QMessageBox, QHeaderView,
                            QCheckBox, QFileDialog, QTabWidget, QWidget, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction

class PluginDialog(QDialog):
    """
    Dialog for managing plugins.
    """
    
    def __init__(self, app_controller):
        """Initialize the plugin dialog."""
        super().__init__()
        self.app_controller = app_controller
        
        # Set properties
        self.setWindowTitle("Plugins")
        self.setMinimumSize(800, 500)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_installed_tab()
        self._create_store_tab()
        self._create_developer_tab()
        
        # Create buttons
        self._create_buttons()
        
        # Load plugins
        self._load_plugins()
    
    def _create_installed_tab(self):
        """Create installed plugins tab."""
        installed_tab = QWidget()
        installed_layout = QVBoxLayout(installed_tab)
        
        # Create plugins table
        self.plugins_table = QTableWidget()
        self.plugins_table.setColumnCount(5)
        self.plugins_table.setHorizontalHeaderLabels(["Name", "Version", "Author", "Description", "Enabled"])
        self.plugins_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.plugins_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.plugins_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.plugins_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.plugins_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.plugins_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.plugins_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.plugins_table.customContextMenuRequested.connect(self._on_context_menu)
        self.plugins_table.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        installed_layout.addWidget(self.plugins_table)
        
        # Add tab
        self.tab_widget.addTab(installed_tab, "Installed Plugins")
    
    def _create_store_tab(self):
        """Create plugin store tab."""
        store_tab = QWidget()
        store_layout = QVBoxLayout(store_tab)
        
        # Create store table
        self.store_table = QTableWidget()
        self.store_table.setColumnCount(5)
        self.store_table.setHorizontalHeaderLabels(["Name", "Version", "Author", "Description", "Action"])
        self.store_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.store_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.store_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.store_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.store_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.store_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        store_layout.addWidget(self.store_table)
        
        # Add tab
        self.tab_widget.addTab(store_tab, "Plugin Store")
    
    def _create_developer_tab(self):
        """Create developer tab."""
        developer_tab = QWidget()
        developer_layout = QVBoxLayout(developer_tab)
        
        # Create developer tools
        developer_layout.addWidget(QLabel("Plugin Development Tools"))
        
        # Create plugin API documentation
        api_label = QLabel("Plugin API Documentation:")
        developer_layout.addWidget(api_label)
        
        self.api_text = QTextEdit()
        self.api_text.setReadOnly(True)
        self.api_text.setPlainText(self._get_api_documentation())
        developer_layout.addWidget(self.api_text)
        
        # Create plugin template button
        template_button = QPushButton("Create Plugin Template")
        template_button.clicked.connect(self._on_create_template)
        developer_layout.addWidget(template_button)
        
        # Add tab
        self.tab_widget.addTab(developer_tab, "Developer")
    
    def _create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Install button
        self.install_button = QPushButton("Install from File...")
        self.install_button.clicked.connect(self._on_install_from_file)
        button_layout.addWidget(self.install_button)
        
        # Reload button
        self.reload_button = QPushButton("Reload All")
        self.reload_button.clicked.connect(self._on_reload_all)
        button_layout.addWidget(self.reload_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(button_layout)
    
    def _load_plugins(self):
        """Load plugins from plugin manager."""
        # Clear table
        self.plugins_table.setRowCount(0)
        
        # Get plugins
        plugins = self.app_controller.plugin_manager.get_plugins()
        
        # Add plugins to table
        for i, (plugin_id, plugin_info) in enumerate(plugins.items()):
            self.plugins_table.insertRow(i)
            
            # Get plugin details
            name = plugin_info.get("name", "Unknown Plugin")
            version = plugin_info.get("version", "1.0.0")
            author = plugin_info.get("author", "Unknown")
            description = plugin_info.get("description", "No description available")
            enabled = plugin_info.get("enabled", False)
            
            # Name
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.ItemDataRole.UserRole, plugin_id)
            self.plugins_table.setItem(i, 0, name_item)
            
            # Version
            version_item = QTableWidgetItem(version)
            self.plugins_table.setItem(i, 1, version_item)
            
            # Author
            author_item = QTableWidgetItem(author)
            self.plugins_table.setItem(i, 2, author_item)
            
            # Description
            description_item = QTableWidgetItem(description)
            self.plugins_table.setItem(i, 3, description_item)
            
            # Enabled
            enabled_check = QCheckBox()
            enabled_check.setChecked(enabled)
            enabled_check.stateChanged.connect(lambda state, pid=plugin_id: self._on_plugin_enabled_changed(pid, state))
            self.plugins_table.setCellWidget(i, 4, enabled_check)
        
        # Load store plugins
        self._load_store_plugins()
    
    def _load_store_plugins(self):
        """Load plugins from plugin store."""
        # Clear table
        self.store_table.setRowCount(0)
        
        # Get store plugins
        store_plugins = self.app_controller.plugin_manager.get_store_plugins()
        
        # Add plugins to table
        for i, plugin in enumerate(store_plugins):
            self.store_table.insertRow(i)
            
            # Get plugin details
            name = plugin.get("name", "Unknown Plugin")
            plugin_id = plugin.get("id", f"unknown_{i}")
            version = plugin.get("version", "1.0.0")
            author = plugin.get("author", "Unknown")
            
            # Name
            name_item = QTableWidgetItem(name)
            name_item.setData(Qt.ItemDataRole.UserRole, plugin_id)
            self.store_table.setItem(i, 0, name_item)
            
            # Version
            version_item = QTableWidgetItem(version)
            self.store_table.setItem(i, 1, version_item)
            
            # Author
            author_item = QTableWidgetItem(author)
            self.store_table.setItem(i, 2, author_item)
            
            # Description
            description_item = QTableWidgetItem(plugin["description"])
            self.store_table.setItem(i, 3, description_item)
            
            # Install button
            install_button = QPushButton("Install")
            install_button.clicked.connect(lambda checked=False, plugin_id=plugin["id"]: self._on_install_plugin(plugin_id))
            self.store_table.setCellWidget(i, 4, install_button)
    
    def _get_api_documentation(self):
        """Get plugin API documentation."""
        return """
NebulaFusion Plugin API Documentation

Plugin Structure:
- Each plugin must be a Python package with an __init__.py file
- The package must contain a manifest.json file with plugin metadata
- The __init__.py file must define a Plugin class that inherits from PluginBase

Manifest Format:
{
    "id": "unique_plugin_id",
    "name": "Plugin Name",
    "version": "1.0.0",
    "author": "Author Name",
    "description": "Plugin description",
    "permissions": ["tabs", "bookmarks", "history", "downloads", "cookies", "storage"]
}

Plugin Class:
class Plugin(PluginBase):
    def __init__(self, api):
        super().__init__(api)
        # Initialize plugin
    
    def activate(self):
        # Called when plugin is activated
        # Register hooks here
        return True
    
    def deactivate(self):
        # Called when plugin is deactivated
        # Unregister hooks here
        return True

Available Hooks:
- onBrowserStart: Called when browser starts
- onBrowserExit: Called when browser exits
- onTabCreated: Called when a new tab is created
- onTabClosed: Called when a tab is closed
- onTabSelected: Called when a tab is selected
- onPageLoading: Called when a page starts loading
- onPageLoaded: Called when a page finishes loading
- onUrlChanged: Called when URL changes
- onDownloadStart: Called when a download starts
- onDownloadProgress: Called during download progress
- onDownloadComplete: Called when a download completes
- onDownloadError: Called when a download fails
- onDownloadCanceled: Called when a download is canceled
- onBookmarkAdded: Called when a bookmark is added
- onBookmarkRemoved: Called when a bookmark is removed
- onHistoryAdded: Called when a history entry is added
- onContextMenu: Called when context menu is shown
- onToolbarCreated: Called when toolbar is created
- onSettingsChanged: Called when settings change
- onRealityAugmentation: Called when reality augmentation is activated
- onCollaborativeSession: Called when collaborative session is started
- onContentTransform: Called when content transformation is requested
- onTimeTravelSnapshot: Called when time travel snapshot is created
- onDimensionalTabChange: Called when dimensional tab changes
- onVoiceCommand: Called when voice command is received

Plugin API:
- tabs: Access to browser tabs
- bookmarks: Access to bookmarks
- history: Access to browsing history
- downloads: Access to downloads
- cookies: Access to cookies
- storage: Access to plugin storage
- settings: Access to browser settings
- ui: Access to browser UI elements
- hooks: Register and unregister hooks
- network: Make network requests
- filesystem: Access filesystem (sandboxed)
- reality: Access reality augmentation features
- collaboration: Access collaborative browsing features
- transformation: Access content transformation features
- timetravel: Access time-travel browsing features
- dimensions: Access dimensional tabs features
- voice: Access voice command features

For more detailed documentation, see the Plugin Developer Guide.
"""
    
    def _on_context_menu(self, pos):
        """Handle context menu event."""
        # Get selected items
        selected_items = self.plugins_table.selectedItems()
        if not selected_items:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Enable action
        enable_action = QAction("Enable", menu)
        enable_action.triggered.connect(lambda: self._on_enable_plugin())
        menu.addAction(enable_action)
        
        # Disable action
        disable_action = QAction("Disable", menu)
        disable_action.triggered.connect(lambda: self._on_disable_plugin())
        menu.addAction(disable_action)
        
        menu.addSeparator()
        
        # Configure action
        configure_action = QAction("Configure", menu)
        configure_action.triggered.connect(lambda: self._on_configure_plugin())
        menu.addAction(configure_action)
        
        # Reload action
        reload_action = QAction("Reload", menu)
        reload_action.triggered.connect(lambda: self._on_reload_plugin())
        menu.addAction(reload_action)
        
        menu.addSeparator()
        
        # Uninstall action
        uninstall_action = QAction("Uninstall", menu)
        uninstall_action.triggered.connect(lambda: self._on_uninstall_plugin())
        menu.addAction(uninstall_action)
        
        # Show menu
        menu.exec(self.plugins_table.mapToGlobal(pos))
    
    def _on_item_double_clicked(self, item):
        """Handle item double clicked event."""
        # Configure plugin
        self._on_configure_plugin()
    
    def _on_enable_plugin(self):
        """Handle enable plugin action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.plugins_table.selectedItems())
        if not selected_rows:
            return
        
        # Enable plugins
        for row in selected_rows:
            plugin_id = self.plugins_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.app_controller.plugin_manager.enable_plugin(plugin_id)
            
            # Update checkbox
            enabled_check = self.plugins_table.cellWidget(row, 4)
            if enabled_check:
                enabled_check.setChecked(True)
    
    def _on_disable_plugin(self):
        """Handle disable plugin action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.plugins_table.selectedItems())
        if not selected_rows:
            return
        
        # Disable plugins
        for row in selected_rows:
            plugin_id = self.plugins_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.app_controller.plugin_manager.disable_plugin(plugin_id)
            
            # Update checkbox
            enabled_check = self.plugins_table.cellWidget(row, 4)
            if enabled_check:
                enabled_check.setChecked(False)
    
    def _on_configure_plugin(self):
        """Handle configure plugin action."""
        # Get selected row
        selected_rows = set(item.row() for item in self.plugins_table.selectedItems())
        if not selected_rows:
            return
        
        # Get plugin ID from first selected row
        row = list(selected_rows)[0]
        plugin_id = self.plugins_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Configure plugin
        self.app_controller.plugin_manager.configure_plugin(plugin_id)
    
    def _on_reload_plugin(self):
        """Handle reload plugin action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.plugins_table.selectedItems())
        if not selected_rows:
            return
        
        # Reload plugins
        for row in selected_rows:
            plugin_id = self.plugins_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.app_controller.plugin_manager.reload_plugin(plugin_id)
    
    def _on_uninstall_plugin(self):
        """Handle uninstall plugin action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.plugins_table.selectedItems())
        if not selected_rows:
            return
        
        # Confirm uninstallation
        result = QMessageBox.question(
            self,
            "Uninstall Plugins",
            f"Are you sure you want to uninstall {len(selected_rows)} plugins?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Uninstall plugins
            for row in sorted(selected_rows, reverse=True):
                plugin_id = self.plugins_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                self.app_controller.plugin_manager.uninstall_plugin(plugin_id)
                self.plugins_table.removeRow(row)
    
    def _on_plugin_enabled_changed(self, plugin_id, state):
        """Handle plugin enabled state changed event."""
        # Enable or disable plugin
        if state == Qt.CheckState.Checked:
            self.app_controller.plugin_manager.enable_plugin(plugin_id)
        else:
            self.app_controller.plugin_manager.disable_plugin(plugin_id)
    
    def _on_install_from_file(self):
        """Handle install from file button click."""
        # Show file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Install Plugin",
            "",
            "Python Packages (*.zip *.whl);;All Files (*.*)"
        )
        
        if file_path:
            # Install plugin
            success = self.app_controller.plugin_manager.install_plugin(file_path)
            
            if success:
                # Reload plugins
                self._load_plugins()
                
                # Show success message
                QMessageBox.information(
                    self,
                    "Plugin Installed",
                    "Plugin installed successfully.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                # Show error message
                QMessageBox.critical(
                    self,
                    "Installation Failed",
                    "Failed to install plugin.",
                    QMessageBox.StandardButton.Ok
                )
    
    def _on_reload_all(self):
        """Handle reload all button click."""
        # Reload all plugins
        self.app_controller.plugin_manager.reload_all_plugins()
        
        # Reload plugins
        self._load_plugins()
    
    def _on_install_plugin(self, plugin_id):
        """Handle install plugin button click."""
        # Install plugin
        success = self.app_controller.plugin_manager.install_store_plugin(plugin_id)
        
        if success:
            # Reload plugins
            self._load_plugins()
            
            # Show success message
            QMessageBox.information(
                self,
                "Plugin Installed",
                "Plugin installed successfully.",
                QMessageBox.StandardButton.Ok
            )
        else:
            # Show error message
            QMessageBox.critical(
                self,
                "Installation Failed",
                "Failed to install plugin.",
                QMessageBox.StandardButton.Ok
            )
    
    def _on_create_template(self):
        """Handle create template button click."""
        # Show file dialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Plugin Directory",
            ""
        )
        
        if directory:
            # Create plugin template
            success = self.app_controller.plugin_manager.create_plugin_template(directory)
            
            if success:
                # Show success message
                QMessageBox.information(
                    self,
                    "Template Created",
                    f"Plugin template created in {directory}.",
                    QMessageBox.StandardButton.Ok
                )
            else:
                # Show error message
                QMessageBox.critical(
                    self,
                    "Template Creation Failed",
                    "Failed to create plugin template.",
                    QMessageBox.StandardButton.Ok
                )
