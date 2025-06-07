#!/usr/bin/env python3
# NebulaFusion Browser - Main Window (FULL CORRECTED COMBINED VERSION)

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QToolBar,
    QLineEdit,
    QMessageBox,
)
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt

# Import your dialogs
from src.ui.plugin_dialog import PluginDialog
from src.ui.history_dialog import HistoryDialog
from src.ui.bookmarks_dialog import BookmarksDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.status_bar import StatusBar
from src.ui.toolbar import Toolbar


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

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_address_bar)
        self.layout.addWidget(self.tab_widget)

        # Plugin / Manager dialogs
        self.plugin_manager_dialog = PluginDialog(self.app_controller)
        self.history_dialog = HistoryDialog(self.app_controller)
        self.bookmarks_dialog = BookmarksDialog(self.app_controller)
        self.settings_dialog = SettingsDialog(self.app_controller)
        self.downloads_dialog = None  # Will be created when needed

        # Status bar
        self.status_bar = StatusBar(self.app_controller)
        self.setStatusBar(self.status_bar)

        # Open initial tab
        self.add_new_tab(QUrl("https://www.google.com"), "New Tab")

        self.app_controller.logger.info(
            "Main window fully initialized with tabbed browsing and managers."
        )

    def add_new_tab(self, url, label="New Tab"):
        browser = QWebEngineView()
        browser.setUrl(url)

        index = self.tab_widget.addTab(browser, label)
        self.tab_widget.setCurrentIndex(index)

        self.app_controller.hook_registry.trigger_hook("onTabCreated", tab=browser)

        # Connect signals
        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.update_url(qurl, browser)
        )
        browser.loadFinished.connect(
            lambda _, browser=browser: self.update_tab_title(browser)
        )

        # Trigger plugin hook
        self.app_controller.hook_registry.trigger_hook("onTabCreated")

        self.app_controller.logger.info(f"New tab opened: {url.toString()}")

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
            url = browser.url().toString()
            self.address_bar.setText(url)

    def update_url(self, qurl, browser):
        if browser == self.current_browser():
            self.address_bar.setText(qurl.toString())

    def update_tab_title(self, browser):
        index = self.tab_widget.indexOf(browser)
        if index != -1:
            self.tab_widget.setTabText(index, browser.title())

    def current_browser(self):
        return self.tab_widget.currentWidget()

    def close_tab(self, index):
        if self.tab_widget.count() < 2:
            QMessageBox.warning(self, "Warning", "Cannot close the last tab.")
            return
        self.tab_widget.removeTab(index)
        self.app_controller.logger.info(f"Tab closed: {index}")
        self.app_controller.hook_registry.trigger_hook("onTabClosed")

        # Trigger plugin hook
        self.app_controller.hook_registry.trigger_hook("onTabClosed")

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
