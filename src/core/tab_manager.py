#!/usr/bin/env python3
# NebulaFusion Browser - Tab Manager

import os
import sys
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

class TabManager(QObject):
    """
    Manager for browser tabs.
    Handles tab creation, deletion, and navigation.
    """
    
    # Signals
    tab_created = pyqtSignal(int, object)  # tab_index, tab
    tab_closed = pyqtSignal(int)  # tab_index
    tab_selected = pyqtSignal(int)  # tab_index
    tab_url_changed = pyqtSignal(int, QUrl)  # tab_index, url
    tab_title_changed = pyqtSignal(int, str)  # tab_index, title
    tab_icon_changed = pyqtSignal(int, object)  # tab_index, icon
    tab_security_changed = pyqtSignal(int, dict)  # tab_index, security_status
    page_loading = pyqtSignal(int)  # tab_index
    page_loaded = pyqtSignal(int, bool)  # tab_index, success
    page_load_progress = pyqtSignal(int, int)  # tab_index, progress
    
    def __init__(self, app_controller):
        """Initialize the tab manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Tabs
        self.tabs = []
        
        # Current tab index
        self.current_tab_index = -1
    
    def initialize(self):
        """Initialize the tab manager."""
        self.app_controller.logger.info("Initializing tab manager...")
        
        # Connect to settings manager
        self.app_controller.settings_manager.setting_changed.connect(self._on_setting_changed)
        
        self.app_controller.logger.info("Tab manager initialized.")
    
    def new_tab(self, url=None, private=False):
        """Create a new tab."""
        # Create tab
        from src.ui.browser_tabs import BrowserTab
        tab = BrowserTab(self.app_controller, private)
        
        # Add tab to list
        self.tabs.append(tab)
        tab_index = len(self.tabs) - 1
        
        # Connect tab signals
        self._connect_tab_signals(tab, tab_index)
        
        # Emit signal
        self.tab_created.emit(tab_index, tab)
        
        # Select tab
        self.select_tab(tab_index)
        
        # Navigate to URL
        if url:
            tab.navigate(url)
        else:
            # Navigate to home page
            home_page = self.app_controller.settings_manager.get_setting("home_page", "https://www.google.com")
            tab.navigate(home_page)
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onTabCreated", tab_index, tab.url().toString())
        
        return tab_index
    
    def close_tab(self, tab_index):
        """Close a tab."""
        # Check if tab exists
        if tab_index < 0 or tab_index >= len(self.tabs):
            return False
        
        # Get tab
        tab = self.tabs[tab_index]
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onTabClosed", tab_index, tab.url().toString())
        
        # Remove tab from list
        self.tabs.pop(tab_index)
        
        # Emit signal
        self.tab_closed.emit(tab_index)
        
        # Update current tab index
        if self.current_tab_index == tab_index:
            # Select another tab
            if len(self.tabs) > 0:
                # Select the tab to the left, or the first tab if this was the first tab
                new_index = max(0, tab_index - 1)
                self.select_tab(new_index)
            else:
                # No tabs left
                self.current_tab_index = -1
        elif self.current_tab_index > tab_index:
            # Adjust current tab index
            self.current_tab_index -= 1
        
        # Delete tab
        tab.deleteLater()
        
        return True
    
    def close_all_tabs(self):
        """Close all tabs."""
        # Close tabs in reverse order
        for i in range(len(self.tabs) - 1, -1, -1):
            self.close_tab(i)
    
    def select_tab(self, tab_index):
        """Select a tab."""
        # Check if tab exists
        if tab_index < 0 or tab_index >= len(self.tabs):
            return False
        
        # Update current tab index
        self.current_tab_index = tab_index
        
        # Emit signal
        self.tab_selected.emit(tab_index)
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onTabSelected", tab_index, self.tabs[tab_index].url().toString())
        
        return True
    
    def get_current_tab(self):
        """Get the current tab."""
        if self.current_tab_index >= 0 and self.current_tab_index < len(self.tabs):
            return self.tabs[self.current_tab_index]
        return None
    
    def get_tab(self, tab_index):
        """Get a tab by index."""
        if tab_index >= 0 and tab_index < len(self.tabs):
            return self.tabs[tab_index]
        return None
    
    def get_tab_count(self):
        """Get the number of tabs."""
        return len(self.tabs)
    
    def navigate_current_tab(self, url):
        """Navigate the current tab to a URL."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.navigate(url)
            return True
        return False
    
    def navigate_tab(self, tab_index, url):
        """Navigate a tab to a URL."""
        tab = self.get_tab(tab_index)
        if tab:
            tab.navigate(url)
            return True
        return False
    
    def reload_current_tab(self):
        """Reload the current tab."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.reload()
            return True
        return False
    
    def reload_tab(self, tab_index):
        """Reload a tab."""
        tab = self.get_tab(tab_index)
        if tab:
            tab.reload()
            return True
        return False
    
    def stop_current_tab(self):
        """Stop loading the current tab."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.stop()
            return True
        return False
    
    def stop_tab(self, tab_index):
        """Stop loading a tab."""
        tab = self.get_tab(tab_index)
        if tab:
            tab.stop()
            return True
        return False
    
    def back_current_tab(self):
        """Go back in the current tab."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.back()
            return True
        return False
    
    def back_tab(self, tab_index):
        """Go back in a tab."""
        tab = self.get_tab(tab_index)
        if tab:
            tab.back()
            return True
        return False
    
    def forward_current_tab(self):
        """Go forward in the current tab."""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.forward()
            return True
        return False
    
    def forward_tab(self, tab_index):
        """Go forward in a tab."""
        tab = self.get_tab(tab_index)
        if tab:
            tab.forward()
            return True
        return False
    
    def _connect_tab_signals(self, tab, tab_index):
        """Connect tab signals."""
        # Title changed
        tab.title_changed.connect(lambda title: self._on_tab_title_changed(tab_index, title))
        
        # URL changed
        tab.url_changed.connect(lambda url: self._on_tab_url_changed(tab_index, url))
        
        # Icon changed
        tab.icon_changed.connect(lambda icon: self._on_tab_icon_changed(tab_index, icon))
        
        # Loading started
        tab.loading_started.connect(lambda: self._on_tab_loading_started(tab_index))
        
        # Loading finished
        tab.loading_finished.connect(lambda success: self._on_tab_loading_finished(tab_index, success))
        
        # Loading progress
        tab.loading_progress.connect(lambda progress: self._on_tab_loading_progress(tab_index, progress))
    
    def _on_tab_title_changed(self, tab_index, title):
        """Handle tab title changed event."""
        # Emit signal
        self.tab_title_changed.emit(tab_index, title)
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onTabTitleChanged", tab_index, title)
    
    def _on_tab_url_changed(self, tab_index, url):
        """Handle tab URL changed event."""
        # Emit signal
        self.tab_url_changed.emit(tab_index, url)
        
        # Check security
        self._check_url_security(tab_index, url)
        
        # Add to history
        tab = self.get_tab(tab_index)
        if tab and not tab.private:
            self.app_controller.history_manager.add_history(url.toString(), tab.title())
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onTabUrlChanged", tab_index, url.toString())
    
    def _on_tab_icon_changed(self, tab_index, icon):
        """Handle tab icon changed event."""
        # Emit signal
        self.tab_icon_changed.emit(tab_index, icon)
    
    def _on_tab_loading_started(self, tab_index):
        """Handle tab loading started event."""
        # Emit signal
        self.page_loading.emit(tab_index)
        
        # Trigger hook
        tab = self.get_tab(tab_index)
        if tab:
            self.app_controller.hook_registry.trigger_hook("onPageLoading", tab_index, tab.url().toString())
    
    def _on_tab_loading_finished(self, tab_index, success):
        """Handle tab loading finished event."""
        # Emit signal
        self.page_loaded.emit(tab_index, success)
        
        # Trigger hook
        tab = self.get_tab(tab_index)
        if tab:
            self.app_controller.hook_registry.trigger_hook("onPageLoaded", tab_index, tab.url().toString(), success)
    
    def _on_tab_loading_progress(self, tab_index, progress):
        """Handle tab loading progress event."""
        # Emit signal
        self.page_load_progress.emit(tab_index, progress)
    
    def _check_url_security(self, tab_index, url):
        """Check URL security and update tab security status."""
        # Get security status
        security_status = self.app_controller.security_manager.check_url_security(url.toString())
        
        # Emit signal
        self.tab_security_changed.emit(tab_index, security_status)
    
    def _on_setting_changed(self, key, value):
        """Handle setting changed event."""
        # Check if setting affects tabs
        if key == "enable_javascript":
            # Update JavaScript setting for all tabs
            for tab in self.tabs:
                tab.page().settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, value)
        
        elif key == "enable_plugins":
            # Update plugins setting for all tabs
            for tab in self.tabs:
                tab.page().settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, value)
        
        elif key == "security_enable_xss_protection":
            # Update XSS protection setting for all tabs
            for tab in self.tabs:
                tab.page().settings().setAttribute(QWebEngineSettings.WebAttribute.XSSAuditingEnabled, value)
        
        elif key == "enable_developer_tools":
            # Update developer tools setting for all tabs. Some Qt builds may
            # lack the DeveloperExtrasEnabled attribute, so guard against that
            # to avoid AttributeError crashes when toggling the setting.
            attr = getattr(
                QWebEngineSettings.WebAttribute, "DeveloperExtrasEnabled", None
            )
            if attr is not None:
                for tab in self.tabs:
                    try:
                        tab.page().settings().setAttribute(attr, value)
                    except AttributeError:
                        # Guard against Qt builds that expose the enum value but
                        # not the underlying feature.
                        self.app_controller.logger.warning(
                            "Developer tools setting not supported"
                        )
