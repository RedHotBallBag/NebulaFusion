#!/usr/bin/env python3
# NebulaFusion Browser - Bookmarks Dialog

import os
import sys
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QLineEdit,
    QLabel,
    QMenu,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction


class BookmarksDialog(QDialog):
    """
    Dialog for managing bookmarks.
    """

    def __init__(self, app_controller):
        """Initialize the bookmarks dialog."""
        super().__init__()
        self.app_controller = app_controller

        # Set properties
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(600, 400)

        # Create layout
        self.layout = QVBoxLayout(self)

        # Create search bar
        self._create_search_bar()

        # Create bookmarks tree
        self._create_bookmarks_tree()

        # Create buttons
        self._create_buttons()

        # Load bookmarks
        self._load_bookmarks()

    def _create_search_bar(self):
        """Create search bar."""
        search_layout = QHBoxLayout()

        # Search label
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)

        # Search input
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search bookmarks...")
        self.search_edit.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_edit)

        self.layout.addLayout(search_layout)

    def _create_bookmarks_tree(self):
        """Create bookmarks tree."""
        self.bookmarks_tree = QTreeWidget()
        self.bookmarks_tree.setHeaderLabels(["Title", "URL"])
        self.bookmarks_tree.setColumnWidth(0, 250)
        self.bookmarks_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.bookmarks_tree.customContextMenuRequested.connect(self._on_context_menu)
        self.bookmarks_tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.layout.addWidget(self.bookmarks_tree)

    def _create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()

        # New folder button
        self.new_folder_button = QPushButton("New Folder")
        self.new_folder_button.clicked.connect(self._on_new_folder)
        button_layout.addWidget(self.new_folder_button)

        # Import button
        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self._on_import)
        button_layout.addWidget(self.import_button)

        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self._on_export)
        button_layout.addWidget(self.export_button)

        # Spacer
        button_layout.addStretch()

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        self.layout.addLayout(button_layout)

    def _load_bookmarks(self):
        """Load bookmarks from bookmark manager."""
        # Clear tree
        self.bookmarks_tree.clear()

        # Create root items for folders
        folder_items = {}

        # Get folders
        folders = self.app_controller.bookmarks_manager.get_folders()

        # Add folders to tree
        for folder in folders:
            folder_item = QTreeWidgetItem(self.bookmarks_tree)
            folder_item.setText(0, folder)
            folder_item.setIcon(0, QIcon.fromTheme("folder"))
            folder_item.setData(
                0, Qt.ItemDataRole.UserRole, {"type": "folder", "name": folder}
            )
            folder_items[folder] = folder_item

        # Get bookmarks
        bookmarks = self.app_controller.bookmarks_manager.get_bookmarks()

        # Add bookmarks to tree
        for bookmark in bookmarks:
            folder = bookmark.get("folder", "other")

            # Create folder if it doesn't exist
            if folder not in folder_items:
                folder_item = QTreeWidgetItem(self.bookmarks_tree)
                folder_item.setText(0, folder)
                folder_item.setIcon(0, QIcon.fromTheme("folder"))
                folder_item.setData(
                    0, Qt.ItemDataRole.UserRole, {"type": "folder", "name": folder}
                )
                folder_items[folder] = folder_item

            # Add bookmark to folder
            bookmark_item = QTreeWidgetItem(folder_items[folder])
            bookmark_item.setText(0, bookmark["title"])
            bookmark_item.setText(1, bookmark["url"])
            bookmark_item.setIcon(0, QIcon.fromTheme("bookmark-new"))
            bookmark_item.setData(
                0, Qt.ItemDataRole.UserRole, {"type": "bookmark", "id": bookmark["id"]}
            )

        # Expand all folders
        self.bookmarks_tree.expandAll()

    def _on_search(self, text):
        """Handle search text changed event."""
        # If search text is empty, show all bookmarks
        if not text:
            for i in range(self.bookmarks_tree.topLevelItemCount()):
                folder_item = self.bookmarks_tree.topLevelItem(i)
                folder_item.setHidden(False)

                for j in range(folder_item.childCount()):
                    bookmark_item = folder_item.child(j)
                    bookmark_item.setHidden(False)

            return

        # Hide all items that don't match search text
        for i in range(self.bookmarks_tree.topLevelItemCount()):
            folder_item = self.bookmarks_tree.topLevelItem(i)
            folder_visible = False

            for j in range(folder_item.childCount()):
                bookmark_item = folder_item.child(j)

                # Check if bookmark title or URL contains search text
                if (
                    text.lower() in bookmark_item.text(0).lower()
                    or text.lower() in bookmark_item.text(1).lower()
                ):
                    bookmark_item.setHidden(False)
                    folder_visible = True
                else:
                    bookmark_item.setHidden(True)

            # Hide folder if it has no visible bookmarks
            folder_item.setHidden(not folder_visible)

    def _on_context_menu(self, pos):
        """Handle context menu event."""
        # Get item at position
        item = self.bookmarks_tree.itemAt(pos)
        if not item:
            return

        # Get item data
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_type = item_data.get("type")

        # Create context menu
        menu = QMenu(self)

        if item_type == "folder":
            # Folder context menu
            rename_action = QAction("Rename Folder", menu)
            rename_action.triggered.connect(lambda: self._on_rename_folder(item))
            menu.addAction(rename_action)

            delete_action = QAction("Delete Folder", menu)
            delete_action.triggered.connect(lambda: self._on_delete_folder(item))
            menu.addAction(delete_action)

        elif item_type == "bookmark":
            # Bookmark context menu
            open_action = QAction("Open", menu)
            open_action.triggered.connect(lambda: self._on_open_bookmark(item))
            menu.addAction(open_action)

            open_new_tab_action = QAction("Open in New Tab", menu)
            open_new_tab_action.triggered.connect(
                lambda: self._on_open_bookmark_new_tab(item)
            )
            menu.addAction(open_new_tab_action)

            menu.addSeparator()

            edit_action = QAction("Edit", menu)
            edit_action.triggered.connect(lambda: self._on_edit_bookmark(item))
            menu.addAction(edit_action)

            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(lambda: self._on_delete_bookmark(item))
            menu.addAction(delete_action)

        # Show menu
        menu.exec(self.bookmarks_tree.mapToGlobal(pos))

    def _on_item_double_clicked(self, item, column):
        """Handle item double clicked event."""
        # Get item data
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_type = item_data.get("type")

        if item_type == "bookmark":
            # Open bookmark
            self._on_open_bookmark(item)

    def _on_open_bookmark(self, item):
        """Handle open bookmark action."""
        # Get bookmark URL
        url = item.text(1)

        # Navigate to URL
        self.app_controller.tab_manager.navigate_current_tab(url)

        # Close dialog
        self.accept()

    def _on_open_bookmark_new_tab(self, item):
        """Handle open bookmark in new tab action."""
        # Get bookmark URL
        url = item.text(1)

        # Open URL in new tab
        self.app_controller.tab_manager.new_tab(url)

        # Close dialog
        self.accept()

    def _on_edit_bookmark(self, item):
        """Handle edit bookmark action."""
        # Get bookmark data
        bookmark_id = item.data(0, Qt.ItemDataRole.UserRole).get("id")
        title = item.text(0)
        url = item.text(1)

        # Show edit dialog
        # This would typically show a dialog to edit the bookmark
        # For now, just update the bookmark with the same data
        self.app_controller.bookmark_manager.update_bookmark(bookmark_id, url, title)

    def _on_delete_bookmark(self, item):
        """Handle delete bookmark action."""
        # Get bookmark ID
        bookmark_id = item.data(0, Qt.ItemDataRole.UserRole).get("id")

        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete Bookmark",
            "Are you sure you want to delete this bookmark?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            # Delete bookmark
            self.app_controller.bookmark_manager.remove_bookmark(bookmark_id)

            # Reload bookmarks
            self._load_bookmarks()

    def _on_rename_folder(self, item):
        """Handle rename folder action."""
        # Get folder name
        folder_name = item.text(0)

        # Show input dialog
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Folder",
            "Enter new folder name:",
            QLineEdit.EchoMode.Normal,
            folder_name,
        )

        if ok and new_name:
            # Rename folder
            self.app_controller.bookmark_manager.rename_bookmark_folder(
                folder_name, new_name
            )

            # Reload bookmarks
            self._load_bookmarks()

    def _on_delete_folder(self, item):
        """Handle delete folder action."""
        # Get folder name
        folder_name = item.text(0)

        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete Folder",
            f"Are you sure you want to delete the folder '{folder_name}' and all its bookmarks?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            # Delete folder
            self.app_controller.bookmark_manager.remove_bookmark_folder(folder_name)

            # Reload bookmarks
            self._load_bookmarks()

    def _on_new_folder(self):
        """Handle new folder button click."""
        # Show input dialog
        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Enter folder name:", QLineEdit.EchoMode.Normal
        )

        if ok and folder_name:
            # Create folder
            self.app_controller.bookmark_manager.create_bookmark_folder(folder_name)

            # Reload bookmarks
            self._load_bookmarks()

    def _on_import(self):
        """Handle import button click."""
        # This would typically show a file dialog to import bookmarks
        # For now, just log the action
        self.app_controller.logger.info("Import bookmarks action triggered")

    def _on_export(self):
        """Handle export button click."""
        # This would typically show a file dialog to export bookmarks
        # For now, just log the action
        self.app_controller.logger.info("Export bookmarks action triggered")
