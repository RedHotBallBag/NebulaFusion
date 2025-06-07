#!/usr/bin/env python3
# NebulaFusion Browser - Browser Tabs

import os
import sys
from PyQt6.QtWidgets import QTabWidget, QMenu, QTabBar, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction, QContextMenuEvent
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class BrowserTab(QWebEngineView):
    """
    Individual browser tab containing a web view.
    """

    # Signals
    title_changed = pyqtSignal(str)
    url_changed = pyqtSignal(QUrl)
    icon_changed = pyqtSignal(QIcon)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal(bool)
    loading_progress = pyqtSignal(int)

    def __init__(self, app_controller, private=False):
        """Initialize the browser tab."""
        super().__init__()
        self.app_controller = app_controller
        self.private = private

        # Create web profile
        if private:
            # Create off-the-record profile for private browsing
            self.profile = (
                self.app_controller.web_engine_manager.create_private_profile()
            )
        else:
            # Use default profile
            self.profile = self.app_controller.web_engine_manager.get_default_profile()

        # Create web page. Avoid storing it under the name "page" since
        # QWebEngineView already provides a method with that name. Using a
        # separate attribute prevents accidental shadowing and call errors.
        self.web_page = QWebEnginePage(self.profile, self)
        self.setPage(self.web_page)

        # Connect download requests from the profile to the download manager
        try:
            self.profile.downloadRequested.connect(self._on_download_requested)
        except Exception as e:
            # Log error but keep browser functioning
            self.app_controller.logger.error(
                f"Failed to connect downloadRequested signal: {e}"
            )

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect signals."""
        # Page signals
        self.titleChanged.connect(self.title_changed)
        self.urlChanged.connect(self.url_changed)
        self.iconChanged.connect(self.icon_changed)
        self.loadStarted.connect(self.loading_started)
        self.loadFinished.connect(self.loading_finished)
        self.loadProgress.connect(self.loading_progress)

    def _on_download_requested(self, download):
        """Forward download requests to the application's download manager."""
        self.app_controller.download_manager.handle_download(download)

    def navigate(self, url):
        """Navigate to URL."""
        if isinstance(url, str):
            # Convert string to QUrl
            if (
                url.startswith("http://")
                or url.startswith("https://")
                or url.startswith("file://")
            ):
                qurl = QUrl(url)
            else:
                # Assume it's a search or URL without scheme
                if "." in url and " " not in url:
                    # Likely a URL without scheme
                    qurl = QUrl("https://" + url)
                else:
                    # Likely a search query
                    search_engine = self.app_controller.settings_manager.get_setting(
                        "default_search_engine"
                    )
                    if search_engine == "google":
                        qurl = QUrl(
                            "https://www.google.com/search?q=" + url.replace(" ", "+")
                        )
                    elif search_engine == "bing":
                        qurl = QUrl(
                            "https://www.bing.com/search?q=" + url.replace(" ", "+")
                        )
                    elif search_engine == "duckduckgo":
                        qurl = QUrl(
                            "https://duckduckgo.com/?q=" + url.replace(" ", "+")
                        )
                    else:
                        qurl = QUrl(
                            "https://www.google.com/search?q=" + url.replace(" ", "+")
                        )
        else:
            # Already a QUrl
            qurl = url

        # Add to history
        if not self.private:
            self.app_controller.history_manager.add_history(
                qurl.toString(), self.title()
            )

        # Navigate
        self.load(qurl)

    def back(self):
        """Go back in history."""
        self.triggerPageAction(QWebEnginePage.WebAction.Back)

    def forward(self):
        """Go forward in history."""
        self.triggerPageAction(QWebEnginePage.WebAction.Forward)

    def reload(self):
        """Reload page."""
        self.triggerPageAction(QWebEnginePage.WebAction.Reload)

    def stop(self):
        """Stop loading."""
        self.triggerPageAction(QWebEnginePage.WebAction.Stop)

    def zoom_in(self):
        """Zoom in."""
        current_zoom = self.zoomFactor()
        self.setZoomFactor(current_zoom + 0.1)

    def zoom_out(self):
        """Zoom out."""
        current_zoom = self.zoomFactor()
        self.setZoomFactor(max(0.1, current_zoom - 0.1))

    def zoom_reset(self):
        """Reset zoom."""
        self.setZoomFactor(1.0)

    def save_page(self, file_path):
        """Save page to file."""
        self.web_page.save(file_path)

    def print_page(self):
        """Print page."""
        self.triggerPageAction(QWebEnginePage.WebAction.Print)

    def find(self):
        """Find in page."""
        self.triggerPageAction(QWebEnginePage.WebAction.Find)

    def cut(self):
        """Cut selected text."""
        self.triggerPageAction(QWebEnginePage.WebAction.Cut)

    def copy(self):
        """Copy selected text."""
        self.triggerPageAction(QWebEnginePage.WebAction.Copy)

    def paste(self):
        """Paste from clipboard."""
        self.triggerPageAction(QWebEnginePage.WebAction.Paste)

    def undo(self):
        """Undo last action."""
        self.triggerPageAction(QWebEnginePage.WebAction.Undo)

    def redo(self):
        """Redo last undone action."""
        self.triggerPageAction(QWebEnginePage.WebAction.Redo)

    def toggle_inspector(self):
        """Toggle web inspector."""
        self.triggerPageAction(QWebEnginePage.WebAction.InspectElement)

    def contextMenuEvent(self, event):
        """Handle context menu event."""
        # Create context menu
        menu = self.createStandardContextMenu()

        # Add custom actions
        menu.addSeparator()

        # Add bookmark action
        bookmark_action = QAction("Bookmark This Page", menu)
        bookmark_action.triggered.connect(self._on_bookmark_page)
        menu.addAction(bookmark_action)

        # Add reality augmentation action
        reality_action = QAction("Reality Augmentation", menu)
        reality_action.triggered.connect(self._on_reality_augmentation)
        menu.addAction(reality_action)

        # Add content transformation action
        transform_action = QAction("Content Transformation", menu)
        transform_action.triggered.connect(self._on_content_transformation)
        menu.addAction(transform_action)

        # Add plugin context menu items
        self.app_controller.hook_registry.trigger_hook(
            "onContextMenu", menu, self.url().toString()
        )

        # Show menu
        menu.exec(event.globalPos())

    def _on_bookmark_page(self):
        """Handle bookmark page action."""
        url = self.url().toString()
        title = self.title()
        self.app_controller.bookmark_manager.add_bookmark(url, title)

    def _on_reality_augmentation(self):
        """Handle reality augmentation action."""
        # This would typically activate reality augmentation
        # For now, just log the action
        self.app_controller.logger.info("Reality Augmentation action triggered")

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onRealityAugmentation", "activate"
        )

    def _on_content_transformation(self):
        """Handle content transformation action."""
        # This would typically transform content
        # For now, just log the action
        self.app_controller.logger.info("Content Transformation action triggered")

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onContentTransform", "text_to_speech", ""
        )


class BrowserTabs(QTabWidget):
    """
    Tab widget for browser tabs.
    """

    def __init__(self, app_controller):
        """Initialize the browser tabs."""
        super().__init__()
        self.app_controller = app_controller

        # Set properties
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)

        # Add new tab button
        self.setCornerWidget(self._create_new_tab_button())

        # Connect signals
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.currentChanged.connect(self._on_current_changed)

        # Tab context menu
        self.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabBar().customContextMenuRequested.connect(self._on_tab_context_menu)

    def _create_new_tab_button(self):
        """Create new tab button."""
        button = QWidget()
        layout = QVBoxLayout(button)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("+")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button.setToolTip("New Tab")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.mousePressEvent = lambda event: self.app_controller.tab_manager.new_tab()

        return button

    def on_tab_created(self, tab_index, tab):
        """Handle tab created event."""
        # Add tab to widget
        self.addTab(tab, "New Tab")

        # Connect tab signals
        tab.title_changed.connect(
            lambda title: self._on_tab_title_changed(tab_index, title)
        )
        tab.icon_changed.connect(
            lambda icon: self._on_tab_icon_changed(tab_index, icon)
        )

        # Select tab
        self.setCurrentIndex(tab_index)

    def on_tab_closed(self, tab_index):
        """Handle tab closed event."""
        # Remove tab from widget
        self.removeTab(tab_index)

    def on_tab_selected(self, tab_index):
        """Handle tab selected event."""
        # Select tab
        self.setCurrentIndex(tab_index)

    def _on_tab_close_requested(self, tab_index):
        """Handle tab close requested event."""
        # Close tab
        self.app_controller.tab_manager.close_tab(tab_index)

    def _on_current_changed(self, tab_index):
        """Handle current tab changed event."""
        # Select tab
        self.app_controller.tab_manager.select_tab(tab_index)

    def _on_tab_title_changed(self, tab_index, title):
        """Handle tab title changed event."""
        # Update tab title
        self.setTabText(tab_index, title)
        self.setTabToolTip(tab_index, title)

    def _on_tab_icon_changed(self, tab_index, icon):
        """Handle tab icon changed event."""
        # Update tab icon
        self.setTabIcon(tab_index, icon)

    def _on_tab_context_menu(self, pos):
        """Handle tab context menu event."""
        # Get tab index
        tab_index = self.tabBar().tabAt(pos)
        if tab_index == -1:
            return

        # Create context menu
        menu = QMenu(self)

        # Add actions
        new_tab_action = QAction("New Tab", menu)
        new_tab_action.triggered.connect(
            lambda: self.app_controller.tab_manager.new_tab()
        )
        menu.addAction(new_tab_action)

        close_tab_action = QAction("Close Tab", menu)
        close_tab_action.triggered.connect(
            lambda: self.app_controller.tab_manager.close_tab(tab_index)
        )
        menu.addAction(close_tab_action)

        close_other_tabs_action = QAction("Close Other Tabs", menu)
        close_other_tabs_action.triggered.connect(
            lambda: self._close_other_tabs(tab_index)
        )
        menu.addAction(close_other_tabs_action)

        menu.addSeparator()

        reload_tab_action = QAction("Reload Tab", menu)
        reload_tab_action.triggered.connect(lambda: self._reload_tab(tab_index))
        menu.addAction(reload_tab_action)

        duplicate_tab_action = QAction("Duplicate Tab", menu)
        duplicate_tab_action.triggered.connect(lambda: self._duplicate_tab(tab_index))
        menu.addAction(duplicate_tab_action)

        menu.addSeparator()

        pin_tab_action = QAction("Pin Tab", menu)
        pin_tab_action.triggered.connect(lambda: self._pin_tab(tab_index))
        menu.addAction(pin_tab_action)

        # Show menu
        menu.exec(self.tabBar().mapToGlobal(pos))

    def _close_other_tabs(self, tab_index):
        """Close all tabs except the specified one."""
        # Get tab count
        tab_count = self.count()

        # Close tabs
        for i in range(tab_count - 1, -1, -1):
            if i != tab_index:
                self.app_controller.tab_manager.close_tab(i)

    def _reload_tab(self, tab_index):
        """Reload the specified tab."""
        # Get tab
        tab = self.widget(tab_index)
        if tab:
            tab.reload()

    def _duplicate_tab(self, tab_index):
        """Duplicate the specified tab."""
        # Get tab
        tab = self.widget(tab_index)
        if tab:
            # Create new tab with same URL
            url = tab.url().toString()
            self.app_controller.tab_manager.new_tab(url)

    def _pin_tab(self, tab_index):
        """Pin the specified tab."""
        # This would typically pin the tab
        # For now, just log the action
        self.app_controller.logger.info(f"Pin tab action triggered for tab {tab_index}")
