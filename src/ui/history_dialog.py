#!/usr/bin/env python3
# NebulaFusion Browser - History Dialog

import os
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QPushButton, QLineEdit, QLabel, QMenu, QMessageBox, QHeaderView,
                            QDateEdit, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDate, QDateTime
from PyQt6.QtGui import QIcon, QAction

class HistoryDialog(QDialog):
    """
    Dialog for browsing and managing history.
    """
    
    def __init__(self, app_controller):
        """Initialize the history dialog."""
        super().__init__()
        self.app_controller = app_controller
        
        # Set properties
        self.setWindowTitle("History")
        self.setMinimumSize(700, 500)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create search and filter bar
        self._create_search_bar()
        
        # Create history table
        self._create_history_table()
        
        # Create buttons
        self._create_buttons()
        
        # Load history
        self._load_history()
    
    def _create_search_bar(self):
        """Create search and filter bar."""
        search_layout = QHBoxLayout()
        
        # Search label
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        # Search input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search history...")
        self.search_edit.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_edit)
        
        # Date filter label
        date_label = QLabel("Date:")
        search_layout.addWidget(date_label)
        
        # Date filter combo
        self.date_combo = QComboBox()
        self.date_combo.addItems(["All Time", "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "Custom"])
        self.date_combo.currentIndexChanged.connect(self._on_date_filter_changed)
        search_layout.addWidget(self.date_combo)
        
        # Custom date filter
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setVisible(False)
        self.date_edit.dateChanged.connect(self._on_custom_date_changed)
        search_layout.addWidget(self.date_edit)
        
        self.layout.addLayout(search_layout)
    
    def _create_history_table(self):
        """Create history table."""
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Title", "URL", "Date"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self._on_context_menu)
        self.history_table.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.layout.addWidget(self.history_table)
    
    def _create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()
        
        # Clear history button
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self._on_clear_history)
        button_layout.addWidget(self.clear_button)
        
        # Spacer
        button_layout.addStretch()
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        self.layout.addLayout(button_layout)
    
    def _load_history(self):
        """Load history from history manager."""
        # Clear table
        self.history_table.setRowCount(0)
        
        # Get history
        history = self.app_controller.history_manager.get_history(limit=1000)
        
        # Add history to table
        for i, item in enumerate(history):
            self.history_table.insertRow(i)
            
            # Title
            title_item = QTableWidgetItem(item["title"])
            title_item.setData(Qt.ItemDataRole.UserRole, item["id"])
            self.history_table.setItem(i, 0, title_item)
            
            # URL
            url_item = QTableWidgetItem(item["url"])
            self.history_table.setItem(i, 1, url_item)
            
            # Date
            date = QDateTime.fromSecsSinceEpoch(item["timestamp"]).toString("yyyy-MM-dd hh:mm:ss")
            date_item = QTableWidgetItem(date)
            date_item.setData(Qt.ItemDataRole.UserRole, item["timestamp"])
            self.history_table.setItem(i, 2, date_item)
    
    def _filter_history(self):
        """Filter history based on search text and date filter."""
        search_text = self.search_edit.text().lower()
        date_filter = self.date_combo.currentText()
        
        # Get current date
        current_date = QDate.currentDate()
        
        # Show all rows
        for i in range(self.history_table.rowCount()):
            self.history_table.setRowHidden(i, False)
        
        # Apply search filter
        if search_text:
            for i in range(self.history_table.rowCount()):
                title = self.history_table.item(i, 0).text().lower()
                url = self.history_table.item(i, 1).text().lower()
                
                if search_text not in title and search_text not in url:
                    self.history_table.setRowHidden(i, True)
        
        # Apply date filter
        if date_filter != "All Time":
            for i in range(self.history_table.rowCount()):
                if self.history_table.isRowHidden(i):
                    continue
                
                timestamp = self.history_table.item(i, 2).data(Qt.ItemDataRole.UserRole)
                date = QDateTime.fromSecsSinceEpoch(timestamp).date()
                
                if date_filter == "Today":
                    if date != current_date:
                        self.history_table.setRowHidden(i, True)
                
                elif date_filter == "Yesterday":
                    if date != current_date.addDays(-1):
                        self.history_table.setRowHidden(i, True)
                
                elif date_filter == "Last 7 Days":
                    if date < current_date.addDays(-7):
                        self.history_table.setRowHidden(i, True)
                
                elif date_filter == "Last 30 Days":
                    if date < current_date.addDays(-30):
                        self.history_table.setRowHidden(i, True)
                
                elif date_filter == "Custom":
                    custom_date = self.date_edit.date()
                    if date != custom_date:
                        self.history_table.setRowHidden(i, True)
    
    def _on_search(self, text):
        """Handle search text changed event."""
        self._filter_history()
    
    def _on_date_filter_changed(self, index):
        """Handle date filter changed event."""
        # Show custom date edit if "Custom" is selected
        self.date_edit.setVisible(self.date_combo.currentText() == "Custom")
        
        # Apply filter
        self._filter_history()
    
    def _on_custom_date_changed(self, date):
        """Handle custom date changed event."""
        self._filter_history()
    
    def _on_context_menu(self, pos):
        """Handle context menu event."""
        # Get selected items
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
        
        # Create context menu
        menu = QMenu(self)
        
        # Open action
        open_action = QAction("Open", menu)
        open_action.triggered.connect(self._on_open_selected)
        menu.addAction(open_action)
        
        # Open in new tab action
        open_new_tab_action = QAction("Open in New Tab", menu)
        open_new_tab_action.triggered.connect(self._on_open_selected_new_tab)
        menu.addAction(open_new_tab_action)
        
        menu.addSeparator()
        
        # Copy URL action
        copy_url_action = QAction("Copy URL", menu)
        copy_url_action.triggered.connect(self._on_copy_url)
        menu.addAction(copy_url_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", menu)
        delete_action.triggered.connect(self._on_delete_selected)
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec(self.history_table.mapToGlobal(pos))
    
    def _on_item_double_clicked(self, item):
        """Handle item double clicked event."""
        # Open URL
        self._on_open_selected()
    
    def _on_open_selected(self):
        """Handle open selected action."""
        # Get selected row
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            return
        
        # Get URL from first selected row
        row = list(selected_rows)[0]
        url = self.history_table.item(row, 1).text()
        
        # Navigate to URL
        self.app_controller.tab_manager.navigate_current_tab(url)
        
        # Close dialog
        self.accept()
    
    def _on_open_selected_new_tab(self):
        """Handle open selected in new tab action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            return
        
        # Get URL from first selected row
        row = list(selected_rows)[0]
        url = self.history_table.item(row, 1).text()
        
        # Open URL in new tab
        self.app_controller.tab_manager.new_tab(url)
        
        # Close dialog
        self.accept()
    
    def _on_copy_url(self):
        """Handle copy URL action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            return
        
        # Get URL from first selected row
        row = list(selected_rows)[0]
        url = self.history_table.item(row, 1).text()
        
        # Copy URL to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
    
    def _on_delete_selected(self):
        """Handle delete selected action."""
        # Get selected rows
        selected_rows = set(item.row() for item in self.history_table.selectedItems())
        if not selected_rows:
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete History Items",
            f"Are you sure you want to delete {len(selected_rows)} history items?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Delete history items
            for row in sorted(selected_rows, reverse=True):
                history_id = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                self.app_controller.history_manager.remove_history(history_id)
                self.history_table.removeRow(row)
    
    def _on_clear_history(self):
        """Handle clear history button click."""
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all browsing history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Clear history
            self.app_controller.history_manager.clear_history()
            
            # Reload history
            self._load_history()
