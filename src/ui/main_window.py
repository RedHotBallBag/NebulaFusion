#!/usr/bin/env python3
# NebulaFusion Browser - Main Window (FULL CORRECTED COMBINED VERSION)

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtCore import QUrl

# Import your dialogs
from src.ui.plugin_dialog import PluginDialog
from src.ui.history_dialog import HistoryDialog
from src.ui.bookmarks_dialog import BookmarksDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.status_bar import StatusBar
from src.ui.toolbar import Toolbar
from src.ui.browser_tabs import BrowserTabs


class MainWindow(QMainWindow):
    def __init__(self, app_controller):
        super().__init__()

        self.app_controller = app_controller
        self.setWindowTitle("NebulaFusion Browser")
        self.resize(1200, 800)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        # --- Add persistent toolbar (for plugins and navigation) ---
        self.toolbar = Toolbar(self.app_controller)
        self.toolbar.action_triggered.connect(self.handle_toolbar_action)
        self.addToolBar(self.toolbar)

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        self.layout.addWidget(self.address_bar)

        # Tab widget managed by TabManager
        self.tab_widget = BrowserTabs(self.app_controller)
        self.layout.addWidget(self.tab_widget)

        # Connect TabManager signals to keep UI in sync
        tm = self.app_controller.tab_manager
        tm.tab_created.connect(self.tab_widget.on_tab_created)
        tm.tab_closed.connect(self.tab_widget.on_tab_closed)
        tm.tab_selected.connect(self.tab_widget.on_tab_selected)
        tm.tab_selected.connect(self.update_address_bar)
        tm.tab_url_changed.connect(self._on_tab_url_changed)

        # Plugin / Manager dialogs
        self.plugin_manager_dialog = PluginDialog(self.app_controller)
        self.history_dialog = HistoryDialog(self.app_controller)
        self.bookmarks_dialog = BookmarksDialog(self.app_controller)
        self.settings_dialog = SettingsDialog(self.app_controller)
        self.downloads_dialog = None  # Will be created when needed

        # Status bar
        self.status_bar = StatusBar(self.app_controller)
        self.setStatusBar(self.status_bar)

        # Open initial tab using the tab manager so plugins work correctly
        self.app_controller.tab_manager.new_tab("https://www.google.com")

        self.app_controller.logger.info(
            "Main window fully initialized with tabbed browsing and managers."
        )

    def add_new_tab(self, url, label="New Tab"):
        """Create a new tab using the tab manager."""
        if isinstance(url, QUrl):
            url = url.toString()
        self.app_controller.tab_manager.new_tab(url)

    def handle_toolbar_action(self, action_id):
        """Handle toolbar button clicks."""
        browser = self.current_browser()
        if not browser and action_id not in ["plugins", "settings"]:
            return
            
        if action_id == "back":
            browser.back()
        elif action_id == "forward":
            browser.forward()
        elif action_id == "reload":
            browser.reload()
        elif action_id == "stop":
            browser.stop()
        elif action_id == "home":
            home_url = self.app_controller.settings_manager.get_setting("general.homepage", "https://www.google.com")
            browser.setUrl(QUrl(home_url))
        elif action_id == "bookmark":
            self.show_bookmarks()
        elif action_id == "history":
            self.show_history()
        elif action_id == "downloads":
            self.show_downloads()
        elif action_id == "plugins":
            self.plugin_manager_dialog.show()
        elif action_id == "settings":
            self.show_settings()

    def navigate_to_address(self):
        url_text = self.address_bar.text()
        if not url_text.startswith("http"):
            url_text = "https://" + url_text
        qurl = QUrl(url_text)
        current_browser = self.current_browser()
        if current_browser:
            current_browser.setUrl(qurl)
            self.app_controller.logger.info(f"Navigating to: {qurl.toString()}")

    def update_address_bar(self, index):
        browser = self.current_browser()
        if browser:
            self.address_bar.setText(browser.url().toString())




    def current_browser(self):
        return self.app_controller.tab_manager.get_current_tab()

    def close_tab(self, index):
        if self.tab_widget.count() < 2:
            QMessageBox.warning(self, "Warning", "Cannot close the last tab.")
            return
        self.app_controller.tab_manager.close_tab(index)

    def go_back(self):
        browser = self.current_browser()
        if browser:
            browser.back()

    def go_forward(self):
        browser = self.current_browser()
        if browser:
            browser.forward()

    def reload_page(self):
        browser = self.current_browser()
        if browser:
            browser.reload()

    def _on_tab_url_changed(self, index, url):
        """Update address bar when the current tab URL changes."""
        if index == self.app_controller.tab_manager.current_tab_index:
            self.address_bar.setText(url.toString())

    # Dialog handlers
    def show_plugin_manager(self):
        self.plugin_manager_dialog.show()

    def show_history(self):
        self.history_dialog.show()

    def show_bookmarks(self):
        self.bookmarks_dialog.show()

    def show_settings(self):
        """Show settings dialog."""
        self.settings_dialog.show()
        
    def show_downloads(self):
        """Show downloads dialog."""
        if not hasattr(self, 'downloads_dialog') or not self.downloads_dialog:
            from src.ui.downloads_dialog import DownloadsDialog
            self.downloads_dialog = DownloadsDialog(self.app_controller)
        self.downloads_dialog.show()
