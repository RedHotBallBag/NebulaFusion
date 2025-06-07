#!/usr/bin/env python3
# NebulaFusion Browser - Downloads Dialog

import os
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QProgressBar, QMenu, QMessageBox, QHeaderView,
                            QLabel, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction

class DownloadsDialog(QDialog):
    """
    Dialog for managing downloads.
    """
    
    def __init__(self, app_controller):
        """Initialize the downloads dialog."""
        super().__init__()
        self.app_controller = app_controller
        
        # Set properties
        self.setWindowTitle("Downloads")
        self.setMinimumSize(700, 400)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create downloads table
        self._create_downloads_table()
        
        # Create buttons
        self._create_buttons()
        
        # Load downloads
        self._load_downloads()
        
        # Connect signals
        self._connect_signals()
    
    def _create_downloads_table(self):
        """Create downloads table."""
        self.downloads_table = QTableWidget()
        self.downloads_table.setColumnCount(5)
        self.downloads_table.setHorizontalHeaderLabels(["Name", "Status", "Progress", "Size", "Location"])
        self.downloads_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.downloads_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.downloads_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.downloads_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.downloads_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.downloads_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.downloads_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.downloads_table.customContextMenuRequested.connect(self._on_context_menu)
        self.downloads_table.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.layout.addWidget(self.downloads_table)
    
    def _create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Clear completed button
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_completed_button.clicked.connect(self._on_clear_completed)
        button_layout.addWidget(self.clear_completed_button)
        
        # Open download folder button
        self.open_folder_button = QPushButton("Open Download Folder")
        self.open_folder_button.clicked.connect(self._on_open_download_folder)
        button_layout.addWidget(self.open_folder_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect signals."""
        # Connect to download manager signals
        self.app_controller.download_manager.download_started.connect(self._on_download_started)
        self.app_controller.download_manager.download_progress.connect(self._on_download_progress)
        self.app_controller.download_manager.download_finished.connect(self._on_download_finished)
    
    def _load_downloads(self):
        """Load downloads from download manager."""
        # Clear table
        self.downloads_table.setRowCount(0)
        
        # Get downloads
        downloads = self.app_controller.download_manager.get_downloads()
        
        # Add downloads to table
        for i, download in enumerate(downloads):
            self._add_download_to_table(download)
    
    def _add_download_to_table(self, download):
        """Add download to table."""
        # Insert new row
        row = self.downloads_table.rowCount()
        self.downloads_table.insertRow(row)
        
        # Name
        name_item = QTableWidgetItem(os.path.basename(download["path"]))
        name_item.setData(Qt.ItemDataRole.UserRole, download["id"])
        self.downloads_table.setItem(row, 0, name_item)
        
        # Status
        status_item = QTableWidgetItem(download["status"])
        self.downloads_table.setItem(row, 1, status_item)
        
        # Progress
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(download["progress"])
        self.downloads_table.setCellWidget(row, 2, progress_bar)
        
        # Size
        size_item = QTableWidgetItem(self._format_size(download["size"]))
        self.downloads_table.setItem(row, 3, size_item)
        
        # Location
        location_item = QTableWidgetItem(os.path.dirname(download["path"]))
        self.downloads_table.setItem(row, 4, location_item)
    
    def _format_size(self, size):
        """Format size in bytes to human-readable format."""
        if size < 0:
            return "Unknown"
        
        if size < 1024:
            return f"{size} B"
        
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        
        return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def _find_download_row(self, download_id):
        """Find row index for download ID."""
        for i in range(self.downloads_table.rowCount()):
            item = self.downloads_table.item(i, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == download_id:
                return i
        
        return -1
    
    def _on_download_started(self, download_id, url, path):
        """Handle download started event."""
        # Get download
        download = self.app_controller.download_manager.get_download(download_id)
        if download:
            self._add_download_to_table(download)
    
    def _on_download_progress(self, download_id, received, total):
        """Handle download progress event."""
        # Find download row
        row = self._find_download_row(download_id)
        if row >= 0:
            # Update progress
            progress_bar = self.downloads_table.cellWidget(row, 2)
            if progress_bar:
                if total > 0:
                    percent = int(received * 100 / total)
                    progress_bar.setValue(percent)
                else:
                    progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Update size
            if total > 0:
                size_item = self.downloads_table.item(row, 3)
                if size_item:
                    size_item.setText(f"{self._format_size(received)} / {self._format_size(total)}")
    
    def _on_download_finished(self, download_id, success):
        """Handle download finished event."""
        # Find download row
        row = self._find_download_row(download_id)
        if row >= 0:
            # Update status
            status_item = self.downloads_table.item(row, 1)
            if status_item:
                status_item.setText("Completed" if success else "Failed")
            
            # Update progress
            progress_bar = self.downloads_table.cellWidget(row, 2)
            if progress_bar:
                progress_bar.setRange(0, 100)
                progress_bar.setValue(100 if success else 0)
    
    def _on_context_menu(self, pos):
        """Handle context menu event."""
        # Get selected items
        selected_items = self.downloads_table.selectedItems()
        if not selected_items:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Open file action
        open_action = QAction("Open File", menu)
        open_action.triggered.connect(self._on_open_file)
        menu.addAction(open_action)
        
        # Open containing folder action
        open_folder_action = QAction("Open Containing Folder", menu)
        open_folder_action.triggered.connect(self._on_open_containing_folder)
        menu.addAction(open_folder_action)
        
        menu.addSeparator()
        
        # Copy URL action
        copy_url_action = QAction("Copy Download URL", menu)
        copy_url_action.triggered.connect(self._on_copy_url)
        menu.addAction(copy_url_action)
        
        menu.addSeparator()
        
        # Resume action
        resume_action = QAction("Resume", menu)
        resume_action.triggered.connect(self._on_resume_download)
        menu.addAction(resume_action)
        
        # Pause action
        pause_action = QAction("Pause", menu)
        pause_action.triggered.connect(self._on_pause_download)
        menu.addAction(pause_action)
        
        # Cancel action
        cancel_action = QAction("Cancel", menu)
        cancel_action.triggered.connect(self._on_cancel_download)
        menu.addAction(cancel_action)
        
        menu.addSeparator()
        
        # Remove from list action
        remove_action = QAction("Remove from List", menu)
        remove_action.triggered.connect(self._on_remove_download)
        menu.addAction(remove_action)
        
        # Show menu
        menu.exec(self.downloads_table.mapToGlobal(pos))
    
    def _on_item_double_clicked(self, item):
        """Handle item double clicked event."""
        # Open file
        self._on_open_file()
    
    def _on_open_file(self):
        """Handle open file action."""
        # Get selected row
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Get download ID from first selected row
        row = list(selected_rows)[0]
        download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get download
        download = self.app_controller.download_manager.get_download(download_id)
        if download and download["status"] == "Completed":
            # Open file
            self.app_controller.file_utils.open_file(download["path"])
    
    def _on_open_containing_folder(self):
        """Handle open containing folder action."""
        # Get selected row
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Get download ID from first selected row
        row = list(selected_rows)[0]
        download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get download
        download = self.app_controller.download_manager.get_download(download_id)
        if download:
            # Open containing folder
            self.app_controller.file_utils.open_folder(os.path.dirname(download["path"]))
    
    def _on_copy_url(self):
        """Handle copy URL action."""
        # Get selected row
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Get download ID from first selected row
        row = list(selected_rows)[0]
        download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Get download
        download = self.app_controller.download_manager.get_download(download_id)
        if download:
            # Copy URL to clipboard
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(download["url"])
    
    def _on_resume_download(self):
        """Handle resume download action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Resume downloads
        for row in selected_rows:
            download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.app_controller.download_manager.resume_download(download_id)
    
    def _on_pause_download(self):
        """Handle pause download action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Pause downloads
        for row in selected_rows:
            download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.app_controller.download_manager.pause_download(download_id)
    
    def _on_cancel_download(self):
        """Handle cancel download action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Confirm cancellation
        result = QMessageBox.question(
            self,
            "Cancel Downloads",
            f"Are you sure you want to cancel {len(selected_rows)} downloads?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Cancel downloads
            for row in selected_rows:
                download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                self.app_controller.download_manager.cancel_download(download_id)
    
    def _on_remove_download(self):
        """Handle remove download action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.downloads_table.selectedItems())
        if not selected_rows:
            return
        
        # Confirm removal
        result = QMessageBox.question(
            self,
            "Remove Downloads",
            f"Are you sure you want to remove {len(selected_rows)} downloads from the list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Remove downloads
            for row in sorted(selected_rows, reverse=True):
                download_id = self.downloads_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                self.app_controller.download_manager.remove_download(download_id)
                self.downloads_table.removeRow(row)
    
    def _on_clear_completed(self):
        """Handle clear completed button click."""
        # Confirm removal
        result = QMessageBox.question(
            self,
            "Clear Completed Downloads",
            "Are you sure you want to clear all completed downloads from the list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Clear completed downloads
            self.app_controller.download_manager.clear_completed_downloads()
            
            # Reload downloads
            self._load_downloads()
    
    def _on_open_download_folder(self):
        """Handle open download folder button click."""
        # Get download directory
        download_dir = self.app_controller.settings_manager.get_setting("download_directory")
        
        # Open folder
        self.app_controller.file_utils.open_folder(download_dir)
