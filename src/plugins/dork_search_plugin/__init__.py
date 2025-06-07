#!/usr/bin/env python3
"""NebulaFusion Browser - Dork Search Panel Plugin"""

from urllib.parse import quote_plus
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt

from src.plugins.plugin_base import PluginBase


class DorkSearchDialog(QDialog):
    """Dialog for building and launching dork searches."""

    def __init__(self, api):
        super().__init__(api.app_controller.main_window)
        self.api = api
        self.setWindowTitle("Dork Search Panel")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        layout = QVBoxLayout()

        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("File Extension:"))
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("pdf, docx, txt, ...")
        ext_layout.addWidget(self.ext_input)
        layout.addLayout(ext_layout)

        query_layout = QHBoxLayout()
        query_layout.addWidget(QLabel("Search Query:"))
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("optional keywords")
        query_layout.addWidget(self.query_input)
        layout.addLayout(query_layout)

        button_layout = QHBoxLayout()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.on_search)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(search_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_search(self):
        """Execute the dork search."""
        ext = self.ext_input.text().strip()
        query = self.query_input.text().strip()
        if not ext:
            self.api.ui.show_warning("Dork Search", "Please specify a file extension.")
            return

        search_terms = f"{query} filetype:{ext}".strip()
        encoded = quote_plus(search_terms)
        url = f"https://www.google.com/search?q={encoded}"
        self.api.tabs.new_tab(url)
        self.close()


class Plugin(PluginBase):
    """Plugin implementation for the Dork Search Panel."""

    def __init__(self, api):
        super().__init__(api)
        self.dialog = None

    def activate(self):
        try:
            self.api.hooks.register_hook(
                "onToolbarCreated", self.plugin_id, self.on_toolbar_created
            )
            main_window = getattr(self.api.app_controller, "main_window", None)
            if main_window and getattr(main_window, "toolbar", None):
                self.on_toolbar_created()
            return True
        except Exception as e:
            self.api.logger.error(f"Failed to activate Dork Search Plugin: {e}")
            return False

    def deactivate(self):
        try:
            self.api.hooks.unregister_all_hooks(self.plugin_id)
            return True
        except Exception as e:
            self.api.logger.error(f"Failed to deactivate Dork Search Plugin: {e}")
            return False

    def on_toolbar_created(self):
        """Add toolbar button when the toolbar is available."""
        try:
            self.api.ui.add_toolbar_button(
                button_id="dork_search",
                text="Dork Search",
                tooltip="Open Dork Search Panel",
                callback=self.open_panel,
            )
            self.api.logger.info("Dork Search toolbar button added.")
        except Exception as e:
            self.api.logger.error(f"Error adding Dork Search button: {e}")

    def open_panel(self):
        """Show the dork search dialog."""
        try:
            if self.dialog is None or not self.dialog.isVisible():
                self.dialog = DorkSearchDialog(self.api)
            self.dialog.show()
            self.dialog.raise_()
            self.dialog.activateWindow()
        except Exception as e:
            self.api.logger.error(f"Error opening Dork Search panel: {e}")
