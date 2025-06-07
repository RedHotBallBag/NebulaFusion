#!/usr/bin/env python3
# NebulaFusion Browser - Toolbar

import os
import sys
from PyQt6.QtWidgets import QToolBar, QToolButton, QMenu
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal

class Toolbar(QToolBar):
    """
    Toolbar for NebulaFusion browser.
    Handles toolbar buttons and actions.
    """
    
    # Signals
    action_triggered = pyqtSignal(str)  # action_id
    
    def __init__(self, app_controller):
        """Initialize the toolbar."""
        super().__init__("Navigation")
        self.app_controller = app_controller
        
        # Set properties
        self.setMovable(False)
        # Use larger icons for better visibility
        self.setIconSize(QSize(24, 24))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Create actions
        self._create_actions()
        
        # Add actions to toolbar
        self._add_actions()
        
        # Notify plugins that toolbar is created
        if hasattr(self.app_controller, 'hook_registry'):
            self.app_controller.hook_registry.trigger_hook('onToolbarCreated')
    
    def _create_actions(self):
        """Create toolbar actions."""
        # Create back action
        self.back_action = QAction("Back", self)
        self.back_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/back.svg")))
        self.back_action.setToolTip("Go back one page")
        self.back_action.triggered.connect(lambda: self.action_triggered.emit("back"))
        
        # Create forward action
        self.forward_action = QAction("Forward", self)
        self.forward_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/forward.svg")))
        self.forward_action.setToolTip("Go forward one page")
        self.forward_action.triggered.connect(lambda: self.action_triggered.emit("forward"))
        
        # Create reload action
        self.reload_action = QAction("Reload", self)
        self.reload_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/reload.svg")))
        self.reload_action.setToolTip("Reload current page")
        self.reload_action.triggered.connect(lambda: self.action_triggered.emit("reload"))
        
        # Create stop action
        self.stop_action = QAction("Stop", self)
        self.stop_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/stop.svg")))
        self.stop_action.setToolTip("Stop loading page")
        self.stop_action.triggered.connect(lambda: self.action_triggered.emit("stop"))
        
        # Create home action
        self.home_action = QAction("Home", self)
        self.home_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/home.svg")))
        self.home_action.setToolTip("Go to home page")
        self.home_action.triggered.connect(lambda: self.action_triggered.emit("home"))
        
        # Create bookmark action
        self.bookmark_action = QAction("Bookmark", self)
        self.bookmark_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/bookmark.svg")))
        self.bookmark_action.setToolTip("Bookmark current page")
        self.bookmark_action.triggered.connect(lambda: self.action_triggered.emit("bookmark"))
        
        # Create history action
        self.history_action = QAction("History", self)
        self.history_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/history.svg")))
        self.history_action.setToolTip("View browsing history")
        self.history_action.triggered.connect(lambda: self.action_triggered.emit("history"))
        
        # Create downloads action
        self.downloads_action = QAction("Downloads", self)
        self.downloads_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/download.svg")))
        self.downloads_action.setToolTip("View downloads")
        self.downloads_action.triggered.connect(lambda: self.action_triggered.emit("downloads"))
        
        # Create plugins action
        self.plugins_action = QAction("Plugins", self)
        self.plugins_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/plugins.svg")))
        self.plugins_action.setToolTip("Manage plugins")
        self.plugins_action.triggered.connect(lambda: self.action_triggered.emit("plugins"))
        
        # Create settings action
        self.settings_action = QAction("Settings", self)
        self.settings_action.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/settings.svg")))
        self.settings_action.setToolTip("Open settings")
        self.settings_action.triggered.connect(lambda: self.action_triggered.emit("settings"))
    
    def _add_actions(self):
        """Add actions to toolbar."""
        # Add back button
        self.addAction(self.back_action)
        
        # Add forward button
        self.addAction(self.forward_action)
        
        # Add reload button
        self.addAction(self.reload_action)
        
        # Add stop button
        self.addAction(self.stop_action)
        
        # Add home button
        self.addAction(self.home_action)
        
        # Add separator
        self.addSeparator()
        
        # Add bookmark button
        self.addAction(self.bookmark_action)
        
        # Add history button
        self.addAction(self.history_action)
        
        # Add downloads button
        self.addAction(self.downloads_action)
        
        # Add separator
        self.addSeparator()
        
        # Add plugins button
        self.addAction(self.plugins_action)
        
        # Add settings button
        self.addAction(self.settings_action)
    
    def update_actions(self, can_go_back, can_go_forward, is_loading):
        """Update toolbar actions."""
        # Update back action
        self.back_action.setEnabled(can_go_back)
        
        # Update forward action
        self.forward_action.setEnabled(can_go_forward)
        
        # Update reload/stop actions
        self.reload_action.setVisible(not is_loading)
        self.stop_action.setVisible(is_loading)
    
    def add_plugin_button(self, action):
        """Add a plugin button (QAction) to the toolbar after the last separator."""
        # Find the last separator and insert after it, or just add if not found
        actions = self.actions()
        last_sep = None
        for a in actions:
            if a.isSeparator():
                last_sep = a
        if last_sep:
            self.insertAction(last_sep, action)
        else:
            self.addAction(action)
