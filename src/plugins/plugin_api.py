#!/usr/bin/env python3
# NebulaFusion Browser - Plugin API

import os
from PyQt6.QtCore import QObject


class PluginAPI(QObject):
    """
    API for browser plugins.
    Provides access to browser functionality for plugins.
    """

    def __init__(self, app_controller, plugin_id, manifest):
        """Initialize the plugin API."""
        super().__init__()
        self.app_controller = app_controller
        self.plugin_id = plugin_id
        self.manifest = manifest

        # Initialize API components
        self._initialize_api()

    def _initialize_api(self):
        """Initialize API components."""
        # Logger
        self.logger = PluginLogger(self.app_controller, self.plugin_id)

        # Hooks
        self.hooks = PluginHooks(self.app_controller, self.plugin_id)

        # Tabs
        self.tabs = PluginTabs(self.app_controller, self.plugin_id)

        # Bookmarks
        self.bookmarks = PluginBookmarks(self.app_controller, self.plugin_id)

        # History
        self.history = PluginHistory(self.app_controller, self.plugin_id)

        # Downloads
        self.downloads = PluginDownloads(self.app_controller, self.plugin_id)

        # Cookies
        self.cookies = PluginCookies(self.app_controller, self.plugin_id)

        # Storage
        self.storage = PluginStorage(self.app_controller, self.plugin_id)

        # UI
        self.ui = PluginUI(self.app_controller, self.plugin_id)

        # Network
        self.network = PluginNetwork(self.app_controller, self.plugin_id)

        # Filesystem
        self.filesystem = PluginFilesystem(self.app_controller, self.plugin_id)

        # Settings
        self.settings = PluginSettings(self.app_controller, self.plugin_id)

        # Unique features
        self.reality = PluginReality(self.app_controller, self.plugin_id)
        self.collaboration = PluginCollaboration(self.app_controller, self.plugin_id)
        self.transformation = PluginTransformation(self.app_controller, self.plugin_id)
        self.timetravel = PluginTimeTravel(self.app_controller, self.plugin_id)
        self.dimensions = PluginDimensions(self.app_controller, self.plugin_id)
        self.voice = PluginVoice(self.app_controller, self.plugin_id)

    def has_permission(self, permission):
        """Check if the plugin has a permission."""
        return permission in self.manifest.get("permissions", [])


class PluginLogger:
    """Logger for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin logger."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def debug(self, message):
        """Log a debug message."""
        self.app_controller.logger.debug(f"[Plugin: {self.plugin_id}] {message}")

    def info(self, message):
        """Log an info message."""
        self.app_controller.logger.info(f"[Plugin: {self.plugin_id}] {message}")

    def warning(self, message):
        """Log a warning message."""
        self.app_controller.logger.warning(f"[Plugin: {self.plugin_id}] {message}")

    def error(self, message):
        """Log an error message."""
        self.app_controller.logger.error(f"[Plugin: {self.plugin_id}] {message}")


class PluginHooks:
    """Hooks for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin hooks."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def register_hook(self, hook_name, plugin_id, callback):
        """Register a hook."""
        return self.app_controller.hook_registry.register_hook(
            hook_name, plugin_id, callback
        )

    def unregister_hook(self, hook_name, plugin_id):
        """Unregister a hook."""
        return self.app_controller.hook_registry.unregister_hook(hook_name, plugin_id)

    def unregister_all_hooks(self, plugin_id):
        """Unregister all hooks for a plugin."""
        return self.app_controller.hook_registry.unregister_all_hooks(plugin_id)

    def get_registered_hooks(self, plugin_id=None):
        """Get registered hooks."""
        return self.app_controller.hook_registry.get_registered_hooks(plugin_id)

    def get_available_hooks(self):
        """Get available hooks."""
        return self.app_controller.hook_registry.get_available_hooks()


class PluginTabs:
    """Tabs API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin tabs API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def get_current_tab(self):
        """Get the current tab."""
        return self.app_controller.tab_manager.get_current_tab()

    def get_tab(self, tab_index):
        """Get a tab by index."""
        return self.app_controller.tab_manager.get_tab(tab_index)

    def get_tab_count(self):
        """Get the number of tabs."""
        return self.app_controller.tab_manager.get_tab_count()

    def new_tab(self, url=None, private=False):
        """Create a new tab."""
        return self.app_controller.tab_manager.new_tab(url, private)

    def close_tab(self, tab_index):
        """Close a tab."""
        return self.app_controller.tab_manager.close_tab(tab_index)

    def select_tab(self, tab_index):
        """Select a tab."""
        return self.app_controller.tab_manager.select_tab(tab_index)

    def navigate(self, url, tab_index=None):
        """Navigate a tab to a URL."""
        if tab_index is None:
            return self.app_controller.tab_manager.navigate_current_tab(url)
        else:
            return self.app_controller.tab_manager.navigate_tab(tab_index, url)

    def reload(self, tab_index=None):
        """Reload a tab."""
        if tab_index is None:
            return self.app_controller.tab_manager.reload_current_tab()
        else:
            return self.app_controller.tab_manager.reload_tab(tab_index)

    def stop(self, tab_index=None):
        """Stop loading a tab."""
        if tab_index is None:
            return self.app_controller.tab_manager.stop_current_tab()
        else:
            return self.app_controller.tab_manager.stop_tab(tab_index)

    def back(self, tab_index=None):
        """Go back in a tab."""
        if tab_index is None:
            return self.app_controller.tab_manager.back_current_tab()
        else:
            return self.app_controller.tab_manager.back_tab(tab_index)

    def forward(self, tab_index=None):
        """Go forward in a tab."""
        if tab_index is None:
            return self.app_controller.tab_manager.forward_current_tab()
        else:
            return self.app_controller.tab_manager.forward_tab(tab_index)


class PluginBookmarks:
    """Bookmarks API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin bookmarks API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def add_bookmark(self, url, title, folder="Bookmarks Bar"):
        """Add a bookmark."""
        return self.app_controller.bookmarks_manager.add_bookmark(url, title, folder)

    def remove_bookmark(self, url, folder=None):
        """Remove a bookmark."""
        return self.app_controller.bookmarks_manager.remove_bookmark(url, folder)

    def update_bookmark(self, url, new_url=None, new_title=None, new_folder=None):
        """Update a bookmark."""
        return self.app_controller.bookmarks_manager.update_bookmark(
            url, new_url, new_title, new_folder
        )

    def add_folder(self, folder_name):
        """Add a bookmark folder."""
        return self.app_controller.bookmarks_manager.add_folder(folder_name)

    def remove_folder(self, folder_name):
        """Remove a bookmark folder."""
        return self.app_controller.bookmarks_manager.remove_folder(folder_name)

    def rename_folder(self, old_name, new_name):
        """Rename a bookmark folder."""
        return self.app_controller.bookmarks_manager.rename_folder(old_name, new_name)

    def get_bookmarks(self, folder=None):
        """Get bookmarks."""
        return self.app_controller.bookmarks_manager.get_bookmarks(folder)

    def get_folders(self):
        """Get bookmark folders."""
        return self.app_controller.bookmarks_manager.get_folders()

    def search_bookmarks(self, query):
        """Search bookmarks."""
        return self.app_controller.bookmarks_manager.search_bookmarks(query)


class PluginHistory:
    """History API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin history API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def add_history(self, url, title):
        """Add a URL to history."""
        return self.app_controller.history_manager.add_history(url, title)

    def remove_history(self, url):
        """Remove a URL from history."""
        return self.app_controller.history_manager.remove_history(url)

    def clear_history(self):
        """Clear all history."""
        return self.app_controller.history_manager.clear_history()

    def get_history(self, limit=100, offset=0):
        """Get history entries."""
        return self.app_controller.history_manager.get_history(limit, offset)

    def search_history(self, query, limit=100, offset=0):
        """Search history entries."""
        return self.app_controller.history_manager.search_history(query, limit, offset)

    def get_history_by_date(self, date, limit=100, offset=0):
        """Get history entries for a specific date."""
        return self.app_controller.history_manager.get_history_by_date(
            date, limit, offset
        )

    def get_history_by_domain(self, domain, limit=100, offset=0):
        """Get history entries for a specific domain."""
        return self.app_controller.history_manager.get_history_by_domain(
            domain, limit, offset
        )

    def get_most_visited(self, limit=10):
        """Get most visited URLs."""
        return self.app_controller.history_manager.get_most_visited(limit)

    def get_recent(self, limit=10):
        """Get recent URLs."""
        return self.app_controller.history_manager.get_recent(limit)


class PluginDownloads:
    """Downloads API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin downloads API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def download_url(self, url, path=None):
        """Download a URL."""
        return self.app_controller.download_manager.download_url(url, path)

    def cancel_download(self, download_id):
        """Cancel a download."""
        return self.app_controller.download_manager.cancel_download(download_id)

    def pause_download(self, download_id):
        """Pause a download."""
        return self.app_controller.download_manager.pause_download(download_id)

    def resume_download(self, download_id):
        """Resume a download."""
        return self.app_controller.download_manager.resume_download(download_id)

    def get_download(self, download_id):
        """Get a download by ID."""
        return self.app_controller.download_manager.get_download(download_id)

    def get_downloads(self):
        """Get all downloads."""
        return self.app_controller.download_manager.get_downloads()

    def clear_completed_downloads(self):
        """Clear completed downloads."""
        return self.app_controller.download_manager.clear_completed_downloads()


class PluginCookies:
    """Cookies API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin cookies API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def get_cookies_for_url(self, url):
        """Get cookies for a URL."""
        return self.app_controller.cookies_manager.get_cookies_for_url(url)

    def set_cookie(self, cookie):
        """Set a cookie."""
        return self.app_controller.cookies_manager.set_cookie(cookie)

    def delete_cookie(self, cookie):
        """Delete a cookie."""
        return self.app_controller.cookies_manager.delete_cookie(cookie)

    def delete_cookies_for_url(self, url, name=None):
        """Delete cookies for a URL."""
        return self.app_controller.cookies_manager.delete_cookies_for_url(url, name)

    def delete_all_cookies(self):
        """Delete all cookies."""
        return self.app_controller.cookies_manager.delete_all_cookies()

    def delete_session_cookies(self):
        """Delete session cookies."""
        return self.app_controller.cookies_manager.delete_session_cookies()

    def block_cookies(self, block=True):
        """Block or unblock cookies."""
        return self.app_controller.cookies_manager.block_cookies(block)


class PluginStorage:
    """Storage API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin storage API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

        # Create storage directory
        self.storage_dir = os.path.expanduser(
            f"~/.nebulafusion/plugins/{plugin_id}/storage"
        )
        os.makedirs(self.storage_dir, exist_ok=True)

    def get(self, key, default=None):
        """Get a value from storage."""
        try:
            # Get storage file path
            storage_file = os.path.join(self.storage_dir, "storage.json")

            # Check if file exists
            if not os.path.exists(storage_file):
                return default

            # Load storage
            import json

            with open(storage_file, "r") as f:
                storage = json.load(f)

            # Get value
            return storage.get(key, default)
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error getting value from storage: {e}"
            )
            return default

    def set(self, key, value):
        """Set a value in storage."""
        try:
            # Get storage file path
            storage_file = os.path.join(self.storage_dir, "storage.json")

            # Load storage
            import json

            storage = {}
            if os.path.exists(storage_file):
                with open(storage_file, "r") as f:
                    storage = json.load(f)

            # Set value
            storage[key] = value

            # Save storage
            with open(storage_file, "w") as f:
                json.dump(storage, f, indent=4)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error setting value in storage: {e}"
            )
            return False

    def remove(self, key):
        """Remove a value from storage."""
        try:
            # Get storage file path
            storage_file = os.path.join(self.storage_dir, "storage.json")

            # Check if file exists
            if not os.path.exists(storage_file):
                return True

            # Load storage
            import json

            with open(storage_file, "r") as f:
                storage = json.load(f)

            # Remove value
            if key in storage:
                del storage[key]

            # Save storage
            with open(storage_file, "w") as f:
                json.dump(storage, f, indent=4)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error removing value from storage: {e}"
            )
            return False

    def clear(self):
        """Clear all storage."""
        try:
            # Get storage file path
            storage_file = os.path.join(self.storage_dir, "storage.json")

            # Check if file exists
            if not os.path.exists(storage_file):
                return True

            # Save empty storage
            import json

            with open(storage_file, "w") as f:
                json.dump({}, f, indent=4)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error clearing storage: {e}"
            )
            return False


class PluginUI:
    """
    UI API for plugins.
    Provides methods for creating and managing UI elements from plugins.
    """

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin UI API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

        # Set up logging
        self.logger = getattr(app_controller, "logger", None)
        if not self.logger:
            import logging

            self.logger = logging.getLogger(f"PluginUI-{plugin_id}")
            self.logger.setLevel(logging.INFO)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

        # Store references to created UI elements
        self._toolbar_buttons = {}
        self._menu_items = {}
        self._context_menu_items = {}

        # Plugin toolbar reference
        self.plugin_toolbar = None

        # Connect to plugin toolbar creation signal if available
        if hasattr(app_controller, "main_window") and hasattr(
            app_controller.main_window, "plugin_toolbar_created"
        ):
            app_controller.main_window.plugin_toolbar_created.connect(
                self._on_plugin_toolbar_created
            )

    def connect_main_window(self, main_window):
        """Connect to a newly created main window."""
        try:
            if hasattr(main_window, "plugin_toolbar_created"):
                main_window.plugin_toolbar_created.connect(
                    self._on_plugin_toolbar_created
                )
            if hasattr(main_window, "plugin_toolbar"):
                self._on_plugin_toolbar_created(main_window.plugin_toolbar)
        except Exception as e:
            self.logger.error(f"Error connecting to main window: {e}")

    def _on_plugin_toolbar_created(self, toolbar):
        """Handle plugin toolbar creation event."""
        self.plugin_toolbar = toolbar
        self.logger.info("Plugin toolbar created, processing queued buttons")
        if hasattr(self, "_queued_buttons"):
            queued_buttons = getattr(self, "_queued_buttons", {})
            for button_id, button_info in list(queued_buttons.items()):
                try:
                    self.logger.info(f"Processing queued button: {button_id}")
                    self.add_toolbar_button(button_id=button_id, **button_info)
                    if button_id in self._queued_buttons:
                        del self._queued_buttons[button_id]
                except Exception as e:
                    self.logger.error(
                        f"Error processing queued button {button_id}: {str(e)}",
                        exc_info=True,
                    )
            self._queued_buttons.clear()

    def add_toolbar_button(
        self, button_id, text, icon=None, tooltip=None, callback=None, position=None
    ):
        """
        Add a button to the plugin toolbar.

        Args:
            button_id (str): Unique identifier for the button
            text (str): Button text
            icon (str or QIcon, optional): Path to icon file or QIcon object
            tooltip (str, optional): Button tooltip text
            callback (callable, optional): Function to call when button is clicked
            position (int, optional): Position to insert the button (None for append)

        Returns:
            bool: True if button was added successfully, False otherwise
        """
        try:
            self.logger.info(f"Adding toolbar button: {button_id}")

            # Check if button already exists
            if button_id in self._toolbar_buttons:
                self.logger.warning(f"Button with ID {button_id} already exists")
                return False

            # Get the plugin toolbar
            main_window = getattr(self.app_controller, "main_window", None)
            if not main_window:
                self.logger.error("Main window not available")
                # Queue the button creation for later
                if not hasattr(self, "_queued_buttons"):
                    self._queued_buttons = {}
                self._queued_buttons[button_id] = {
                    "text": text,
                    "icon": icon,
                    "tooltip": tooltip,
                    "callback": callback,
                    "position": position,
                }
                return True

            toolbar = getattr(main_window, "plugin_toolbar", None)
            if not toolbar:
                self.logger.warning(
                    "Plugin toolbar not available, will add button when created"
                )
                if not hasattr(self, "_queued_buttons"):
                    self._queued_buttons = {}
                self._queued_buttons[button_id] = {
                    "text": text,
                    "icon": icon,
                    "tooltip": tooltip,
                    "callback": callback,
                    "position": position,
                }
                return True

            # Create the action
            from PyQt6.QtGui import QIcon, QAction

            action = QAction(text, self.app_controller.main_window)
            action.setObjectName(f"{self.plugin_id}_{button_id}")

            # Set icon if provided
            if icon:
                if isinstance(icon, str):
                    if os.path.exists(icon):
                        action.setIcon(QIcon(icon))
                    else:
                        self.logger.warning(f"Icon file not found: {icon}")
                elif hasattr(icon, "isValid") and callable(icon.isValid):
                    # It's a QIcon
                    action.setIcon(icon)

            # Set tooltip if provided
            if tooltip:
                action.setToolTip(tooltip)
                action.setStatusTip(tooltip)

            # Connect callback if provided
            if callback and callable(callback):
                action.triggered.connect(
                    lambda checked, cb=callback: self._safe_callback(cb)
                )

            # Add action to plugin toolbar
            if hasattr(toolbar, "add_plugin_button"):
                toolbar.add_plugin_button(action)
            else:
                toolbar.addAction(action)

            # Store reference to the action
            self._toolbar_buttons[button_id] = action

            self.logger.info(f"Successfully added toolbar button: {button_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Error adding toolbar button '{button_id}': {str(e)}", exc_info=True
            )
            return False

    def _safe_callback(self, callback):
        """Safely execute a callback with error handling."""
        try:
            self.logger.debug(
                f"Executing callback: {callback.__name__ if hasattr(callback, '__name__') else 'anonymous'}"
            )
            return callback()
        except Exception as e:
            self.logger.error(f"Error in callback: {str(e)}", exc_info=True)

    def remove_toolbar_button(self, button_id):
        """
        Remove a toolbar button.

        Args:
            button_id (str): ID of the button to remove

        Returns:
            bool: True if button was removed, False otherwise
        """
        try:
            if button_id in self._toolbar_buttons:
                button = self._toolbar_buttons[button_id]
                button.setParent(None)
                button.deleteLater()
                del self._toolbar_buttons[button_id]
                self.logger.info(f"Removed toolbar button: {button_id}")
                return True

            # Check if button is in queue
            if hasattr(self, "_queued_buttons") and button_id in self._queued_buttons:
                del self._queued_buttons[button_id]
                self.logger.info(f"Removed queued toolbar button: {button_id}")
                return True

            self.logger.warning(f"Button not found: {button_id}")
            return False

        except Exception as e:
            self.logger.error(
                f"Error removing toolbar button '{button_id}': {str(e)}", exc_info=True
            )
            return False

    def show_message(self, title, message):
        """Show a message dialog."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(None, title, message)
        except Exception as e:
            self.logger.error(f"Error showing message dialog: {str(e)}", exc_info=True)

    def show_error(self, title, message):
        """Show an error dialog."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.critical(None, title, message)
        except Exception as e:
            self.logger.error(f"Error showing error dialog: {str(e)}", exc_info=True)

    def show_warning(self, title, message):
        """Show a warning dialog."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(None, title, message)
        except Exception as e:
            self.logger.error(f"Error showing warning dialog: {str(e)}", exc_info=True)

    def show_question(self, title, message):
        """Show a question dialog."""
        try:
            from PyQt6.QtWidgets import QMessageBox

            return (
                QMessageBox.question(None, title, message)
                == QMessageBox.StandardButton.Yes
            )
        except Exception as e:
            self.logger.error(f"Error showing question dialog: {str(e)}", exc_info=True)
            return False

    def show_input_dialog(self, title, message, default=""):
        """Show an input dialog."""
        try:
            from PyQt6.QtWidgets import QInputDialog

            text, ok = QInputDialog.getText(None, title, message, text=default)
            return text if ok else None
        except Exception as e:
            self.logger.error(f"Error showing input dialog: {str(e)}", exc_info=True)
            return None

    def show_file_dialog(self, title, directory="", filter=""):
        """Show a file dialog."""
        try:
            from PyQt6.QtWidgets import QFileDialog

            return QFileDialog.getOpenFileName(None, title, directory, filter)[0]
        except Exception as e:
            self.logger.error(f"Error showing file dialog: {str(e)}", exc_info=True)
            return ""

    def show_save_dialog(self, title, directory="", filter=""):
        """Show a save dialog."""
        try:
            from PyQt6.QtWidgets import QFileDialog

            return QFileDialog.getSaveFileName(None, title, directory, filter)[0]
        except Exception as e:
            self.logger.error(f"Error showing save dialog: {str(e)}", exc_info=True)
            return ""

    def show_directory_dialog(self, title, directory=""):
        """Show a directory dialog."""
        try:
            from PyQt6.QtWidgets import QFileDialog

            return QFileDialog.getExistingDirectory(None, title, directory)
        except Exception as e:
            self.logger.error(
                f"Error showing directory dialog: {str(e)}", exc_info=True
            )
            return ""

    def add_menu_item(self, menu, text, icon=None, tooltip=None, callback=None):
        """
        Add an item to a menu.

        Args:
            menu: The menu to add the item to
            text (str): The text of the menu item
            icon (QIcon or str, optional): The icon for the menu item
            tooltip (str, optional): Tooltip text
            callback (callable, optional): Function to call when the menu item is triggered

        Returns:
            QAction: The created menu item action, or None if failed
        """
        try:
            from PyQt6.QtGui import QAction, QIcon

            action = QAction(text, None)
            if icon:
                if isinstance(icon, str):
                    if os.path.exists(icon):
                        action.setIcon(QIcon(icon))
                else:
                    action.setIcon(icon)

            if tooltip:
                action.setToolTip(tooltip)

            if callback and callable(callback):
                action.triggered.connect(
                    lambda checked, cb=callback: self._safe_callback(cb)
                )

            menu.addAction(action)

            # Store reference
            if not hasattr(self, "_menu_items"):
                self._menu_items = {}
            self._menu_items[id(action)] = action

            return action

        except Exception as e:
            self.logger.error(f"Error adding menu item: {str(e)}", exc_info=True)
            return None

    def add_context_menu_item(self, text, icon=None, tooltip=None, callback=None):
        """
        Add an item to the browser's context menu.

        Args:
            text (str): The text of the menu item
            icon (QIcon or str, optional): The icon for the menu item
            tooltip (str, optional): Tooltip text
            callback (callable, optional): Function to call when the menu item is triggered

        Returns:
            QAction: The created menu item action, or None if failed
        """
        try:
            main_window = getattr(self.app_controller, "main_window", None)
            if not main_window or not hasattr(main_window, "add_context_menu_action"):
                self.logger.error("Main window or context menu not available")
                return None

            action = self.add_menu_item(None, text, icon, tooltip, callback)
            if action:
                main_window.add_context_menu_action(action)

                # Store reference
                if not hasattr(self, "_context_menu_items"):
                    self._context_menu_items = {}
                self._context_menu_items[id(action)] = action

            return action

        except Exception as e:
            self.logger.error(
                f"Error adding context menu item: {str(e)}", exc_info=True
            )
            return None


class PluginNetwork:
    """Network API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin network API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def get(self, url, headers=None, params=None, timeout=30):
        """Send a GET request."""
        import requests

        try:
            response = requests.get(
                url, headers=headers, params=params, timeout=timeout
            )
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "text": response.text,
                "json": (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else None
                ),
            }
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error sending GET request: {e}"
            )
            return None

    def post(self, url, data=None, json=None, headers=None, timeout=30):
        """Send a POST request."""
        import requests

        try:
            response = requests.post(
                url, data=data, json=json, headers=headers, timeout=timeout
            )
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "text": response.text,
                "json": (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else None
                ),
            }
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error sending POST request: {e}"
            )
            return None

    def put(self, url, data=None, json=None, headers=None, timeout=30):
        """Send a PUT request."""
        import requests

        try:
            response = requests.put(
                url, data=data, json=json, headers=headers, timeout=timeout
            )
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "text": response.text,
                "json": (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else None
                ),
            }
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error sending PUT request: {e}"
            )
            return None

    def delete(self, url, headers=None, timeout=30):
        """Send a DELETE request."""
        import requests

        try:
            response = requests.delete(url, headers=headers, timeout=timeout)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "text": response.text,
                "json": (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else None
                ),
            }
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error sending DELETE request: {e}"
            )
            return None

    def download_file(self, url, path, headers=None, timeout=30):
        """Download a file."""
        import requests

        try:
            response = requests.get(url, headers=headers, timeout=timeout, stream=True)
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error downloading file: {e}"
            )
            return False


class PluginFilesystem:
    """Filesystem API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin filesystem API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

        # Create plugin directory
        self.plugin_dir = os.path.expanduser(f"~/.nebulafusion/plugins/{plugin_id}")
        os.makedirs(self.plugin_dir, exist_ok=True)

    def read_file(self, path, binary=False):
        """Read a file."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Read file
            mode = "rb" if binary else "r"
            with open(path, mode) as f:
                return f.read()
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error reading file: {e}"
            )
            return None

    def write_file(self, path, content, binary=False):
        """Write a file."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Write file
            mode = "wb" if binary else "w"
            with open(path, mode) as f:
                f.write(content)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error writing file: {e}"
            )
            return False

    def append_file(self, path, content, binary=False):
        """Append to a file."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Append to file
            mode = "ab" if binary else "a"
            with open(path, mode) as f:
                f.write(content)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error appending to file: {e}"
            )
            return False

    def delete_file(self, path):
        """Delete a file."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Delete file
            os.remove(path)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error deleting file: {e}"
            )
            return False

    def create_directory(self, path):
        """Create a directory."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Create directory
            os.makedirs(path, exist_ok=True)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error creating directory: {e}"
            )
            return False

    def delete_directory(self, path):
        """Delete a directory."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Delete directory
            import shutil

            shutil.rmtree(path)

            return True
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error deleting directory: {e}"
            )
            return False

    def list_directory(self, path):
        """List a directory."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # List directory
            return os.listdir(path)
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error listing directory: {e}"
            )
            return None

    def file_exists(self, path):
        """Check if a file exists."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Check if file exists
            return os.path.isfile(path)
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error checking if file exists: {e}"
            )
            return False

    def directory_exists(self, path):
        """Check if a directory exists."""
        try:
            # Check if path is absolute
            if not os.path.isabs(path):
                # Make path relative to plugin directory
                path = os.path.join(self.plugin_dir, path)

            # Check if path is within plugin directory
            if not path.startswith(self.plugin_dir):
                raise ValueError("Path must be within plugin directory")

            # Check if directory exists
            return os.path.isdir(path)
        except Exception as e:
            self.app_controller.logger.error(
                f"[Plugin: {self.plugin_id}] Error checking if directory exists: {e}"
            )
            return False


class PluginSettings:
    """Settings API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin settings API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def get_setting(self, key, default=None):
        """Get a setting."""
        return self.app_controller.settings_manager.get_setting(key, default)

    def set_setting(self, key, value):
        """Set a setting."""
        return self.app_controller.settings_manager.set_setting(key, value)

    def get_plugin_setting(self, key, default=None):
        """Get a plugin setting."""
        plugin_key = f"plugin.{self.plugin_id}.{key}"
        return self.app_controller.settings_manager.get_setting(plugin_key, default)

    def set_plugin_setting(self, key, value):
        """Set a plugin setting."""
        plugin_key = f"plugin.{self.plugin_id}.{key}"
        return self.app_controller.settings_manager.set_setting(plugin_key, value)


class PluginReality:
    """Reality augmentation API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin reality augmentation API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def augment_page(self, tab_index, augmentation_data):
        """Augment a page with reality augmentation."""
        # TODO: Implement reality augmentation
        pass

    def remove_augmentation(self, tab_index):
        """Remove reality augmentation from a page."""
        # TODO: Implement reality augmentation
        pass


class PluginCollaboration:
    """Collaboration API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin collaboration API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def start_session(self, session_id=None):
        """Start a collaborative session."""
        # TODO: Implement collaborative browsing
        pass

    def join_session(self, session_id):
        """Join a collaborative session."""
        # TODO: Implement collaborative browsing
        pass

    def leave_session(self):
        """Leave a collaborative session."""
        # TODO: Implement collaborative browsing
        pass

    def send_message(self, message):
        """Send a message to the collaborative session."""
        # TODO: Implement collaborative browsing
        pass


class PluginTransformation:
    """Content transformation API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin content transformation API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def transform_page(self, tab_index, transformation_type, options=None):
        """Transform a page."""
        # TODO: Implement content transformation
        pass

    def reset_transformation(self, tab_index):
        """Reset page transformation."""
        # TODO: Implement content transformation
        pass


class PluginTimeTravel:
    """Time-travel browsing API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin time-travel browsing API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def create_snapshot(self, tab_index, name=None):
        """Create a time-travel snapshot."""
        # TODO: Implement time-travel browsing
        pass

    def get_snapshots(self, tab_index):
        """Get time-travel snapshots."""
        # TODO: Implement time-travel browsing
        pass

    def restore_snapshot(self, tab_index, snapshot_id):
        """Restore a time-travel snapshot."""
        # TODO: Implement time-travel browsing
        pass

    def delete_snapshot(self, tab_index, snapshot_id):
        """Delete a time-travel snapshot."""
        # TODO: Implement time-travel browsing
        pass


class PluginDimensions:
    """Dimensional tabs API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin dimensional tabs API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def create_dimension(self, tab_index, name=None):
        """Create a dimensional tab."""
        # TODO: Implement dimensional tabs
        pass

    def get_dimensions(self, tab_index):
        """Get dimensional tabs."""
        # TODO: Implement dimensional tabs
        pass

    def switch_dimension(self, tab_index, dimension_id):
        """Switch to a dimensional tab."""
        # TODO: Implement dimensional tabs
        pass

    def delete_dimension(self, tab_index, dimension_id):
        """Delete a dimensional tab."""
        # TODO: Implement dimensional tabs
        pass


class PluginVoice:
    """Voice command API for plugins."""

    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin voice command API."""
        self.app_controller = app_controller
        self.plugin_id = plugin_id

    def register_command(self, command, callback):
        """Register a voice command."""
        # TODO: Implement voice commands
        pass

    def unregister_command(self, command):
        """Unregister a voice command."""
        # TODO: Implement voice commands
        pass

    def get_commands(self):
        """Get registered voice commands."""
        # TODO: Implement voice commands
        pass
