#!/usr/bin/env python3
# NebulaFusion Browser - Address Bar

import os
import sys
from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel

class AddressBar(QLineEdit):
    """
    Address bar for NebulaFusion browser.
    Handles URL input and navigation.
    """
    
    # Signals
    url_changed = pyqtSignal(str)  # url
    
    def __init__(self, app_controller):
        """Initialize the address bar."""
        super().__init__()
        self.app_controller = app_controller
        
        # Set properties
        self.setPlaceholderText("Enter URL or search term")
        
        # Create completer
        self.completer = QCompleter()
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self.completer)
        
        # Connect signals
        self.returnPressed.connect(self._on_return_pressed)
    
    def set_url(self, url):
        """Set the URL in the address bar."""
        self.setText(url)
    
    def update_completer(self, urls):
        """Update the completer with a list of URLs."""
        model = QStringListModel()
        model.setStringList(urls)
        self.completer.setModel(model)

    def focusInEvent(self, event):
        """Select all text when the widget gains focus."""
        super().focusInEvent(event)
        self.selectAll()
    
    def _on_return_pressed(self):
        """Handle return key press."""
        # Get URL
        url = self.text()
        
        # Check if URL is valid
        if not url.startswith(("http://", "https://", "file://", "ftp://", "data:")):
            # Check if URL is a local file
            if os.path.exists(url):
                url = f"file://{url}"
            # Check if URL is a domain
            elif "." in url and " " not in url:
                url = f"https://{url}"
            # Treat as search query
            else:
                search_engine = self.app_controller.settings_manager.get_setting("general.search_engine")
                if not search_engine:
                    search_engine = "https://www.google.com/search?q="
                url = f"{search_engine}{url.replace(' ', '+')}"
        
        # Emit signal
        self.url_changed.emit(url)
