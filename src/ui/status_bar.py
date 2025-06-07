#!/usr/bin/env python3
# NebulaFusion Browser - Status Bar

import os
import sys
from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal

class StatusBar(QStatusBar):
    """
    Status bar for browser status information.
    """
    
    def __init__(self, app_controller):
        """Initialize the status bar."""
        super().__init__()
        self.app_controller = app_controller
        
        # Create widgets
        self._create_widgets()
        
        # Connect signals
        self._connect_signals()
    
    def _create_widgets(self):
        """Create status bar widgets."""
        # URL label
        self.url_label = QLabel()
        self.url_label.setTextFormat(Qt.TextFormat.RichText)
        self.addWidget(self.url_label, 1)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(12)
        self.progress_bar.setMaximumWidth(100)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)
        
        # Security label
        self.security_label = QLabel()
        self.addPermanentWidget(self.security_label)
        
        # Download label
        self.download_label = QLabel()
        self.addPermanentWidget(self.download_label)
    
    def _connect_signals(self):
        """Connect signals."""
        pass
    
    def on_page_loading(self):
        """Handle page loading event."""
        # Show progress bar
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Update status
        self.showMessage("Loading...")
    
    def on_page_loaded(self, success):
        """Handle page loaded event."""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        if success:
            self.showMessage("Page loaded", 5000)
        else:
            self.showMessage("Failed to load page", 5000)
    
    def on_page_load_progress(self, progress):
        """Handle page load progress event."""
        # Update progress bar
        self.progress_bar.setValue(progress)
    
    def on_url_changed(self, url):
        """Handle URL changed event."""
        # Update URL label
        self.url_label.setText(f"<small>{url.toString()}</small>")
    
    def on_security_changed(self, security_status):
        """Handle security changed event."""
        # Update security label
        if security_status["is_secure"]:
            self.security_label.setText("🔒 Secure")
            self.security_label.setToolTip("Connection is secure")
        else:
            self.security_label.setText("🔓 Not Secure")
            self.security_label.setToolTip(security_status.get("message", "Connection is not secure"))
    
    def on_download_started(self, download_id, url, path):
        """Handle download started event."""
        # Update download label
        self.download_label.setText("⬇️ Downloading...")
        self.download_label.setToolTip(f"Downloading {os.path.basename(path)}")
    
    def on_download_progress(self, download_id, received, total):
        """Handle download progress event."""
        # Update download label
        if total > 0:
            percent = int(received * 100 / total)
            self.download_label.setText(f"⬇️ {percent}%")
            self.download_label.setToolTip(f"Downloaded {received} of {total} bytes")
    
    def on_download_finished(self, download_id, success):
        """Handle download finished event."""
        # Update download label
        if success:
            self.download_label.setText("✅ Download complete")
            self.download_label.setToolTip("Download completed successfully")
        else:
            self.download_label.setText("❌ Download failed")
            self.download_label.setToolTip("Download failed")
        
        # Clear download label after 5 seconds
        QTimer.singleShot(5000, lambda: self.download_label.setText(""))
