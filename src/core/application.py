#!/usr/bin/env python3
# NebulaFusion Browser - Application

import os
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QSettings

# Import core modules
from src.core.web_engine import WebEngineManager
from src.core.tab_manager import TabManager
from src.core.history import HistoryManager
from src.core.bookmarks import BookmarksManager
from src.core.cookies import CookiesManager
from src.core.downloads import DownloadManager
from src.core.security import SecurityManager
from src.core.content_security import ContentSecurityManager

# Import plugin modules
from src.plugins.plugin_loader import PluginLoader
from src.plugins.plugin_manager import PluginManager
from src.plugins.hook_registry import HookRegistry

# Import theme modules
from src.themes.theme_manager import ThemeManager

# Import UI modules
from src.ui.main_window import MainWindow


class Application(QObject):
    """
    Main application class for NebulaFusion browser.
    Handles initialization, cleanup, and management of browser components.
    """

    # Signals
    initialized = pyqtSignal()  # THIS IS THE SIGNAL. Keep this name.
    starting = pyqtSignal()
    closing = pyqtSignal()

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Application state
        self._is_initialized_flag = (
            False  # CHANGED: Renamed the boolean flag to avoid collision
        )
        self.main_window = None

        # Setup logging
        self._setup_logging()

        # Create managers
        self._create_managers()

    def _setup_logging(self):
        """Setup logging."""
        # Create logger
        self.logger = logging.getLogger("NebulaFusion")
        self.logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(console_handler)

        # Create log directory
        log_dir = os.path.expanduser("~/.nebulafusion/logs")
        os.makedirs(log_dir, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "nebulafusion.log"))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

    def _create_managers(self):
        """Create managers."""
        # Create settings manager
        self.settings_manager = SettingsManager(self)

        # Create web engine manager
        self.web_engine_manager = WebEngineManager(self)

        # Create tab manager
        self.tab_manager = TabManager(self)

        # Create history manager
        self.history_manager = HistoryManager(self)

        # Create bookmarks manager
        self.bookmarks_manager = BookmarksManager(self)

        # Create cookies manager
        self.cookies_manager = CookiesManager(self)

        # Create download manager
        self.download_manager = DownloadManager(self)

        # Create security manager
        self.security_manager = SecurityManager(self)

        # Create content security manager
        self.content_security_manager = ContentSecurityManager(self)

        # Create hook registry
        self.hook_registry = HookRegistry(self)

        # Create plugin loader
        self.plugin_loader = PluginLoader(self)

        # Create plugin manager
        self.plugin_manager = PluginManager(self)

        # Create theme manager
        self.theme_manager = ThemeManager(self)

    def initialize(self):
        """Initialize the application."""
        self.logger.info("Initializing NebulaFusion browser...")

        # Emit starting signal
        self.starting.emit()

        # Initialize core managers first
        self.logger.info("Initializing core managers...")
        self.settings_manager.initialize()
        self.web_engine_manager.initialize()
        self.tab_manager.initialize()
        self.history_manager.initialize()
        self.bookmarks_manager.initialize()
        self.cookies_manager.initialize()
        self.download_manager.initialize()
        self.security_manager.initialize()
        self.content_security_manager.initialize()

        # Initialize hook registry before plugins
        self.logger.info("Initializing hook registry...")
        self.hook_registry.initialize()

        # Initialize plugin system
        self.logger.info("Initializing plugin system...")
        self.plugin_loader.initialize()
        self.plugin_manager.initialize()

        # Load and enable plugins before creating the UI so hooks like
        # onToolbarCreated and onBrowserStart fire correctly during startup.
        self.logger.info("Loading and enabling plugins...")
        self._initialize_plugins()

        # Initialize theme manager
        self.logger.info("Initializing theme manager...")
        self.theme_manager.initialize()

        # Create main window
        self.logger.info("Creating main window...")
        self.main_window = MainWindow(self)

        # Connect plugin UI components now that the main window exists
        for plugin in self.plugin_loader.loaded_plugins.values():
            try:
                plugin["api"].ui.connect_main_window(self.main_window)
            except Exception as e:
                self.logger.error(
                    f"Error connecting plugin {plugin['id']} UI: {e}"
                )

        # Show main window
        if self.main_window:
            self.main_window.show()
            self.logger.info("Main window created and shown.")
        else:
            self.logger.error("Main window could not be created.")
            return False

        # Trigger browser start hook after plugins are enabled
        self.logger.info("Triggering browser start hook...")
        self.hook_registry.trigger_hook("onBrowserStart")

        # Update state
        self._is_initialized_flag = True

        # Emit initialized signal
        self.initialized.emit()
        self.logger.info("NebulaFusion browser initialized.")

        return True

    def _initialize_plugins(self):
        """Initialize and enable all plugins."""
        try:
            # Get all available plugins
            available_plugins = self.plugin_manager.get_available_plugins()
            self.logger.info(f"Found {len(available_plugins)} available plugins")

            # Enable all plugins
            for plugin_id in available_plugins:
                try:
                    self.logger.info(f"Enabling plugin: {plugin_id}")
                    self.plugin_manager.enable_plugin(plugin_id)
                except Exception as e:
                    self.logger.error(f"Error enabling plugin {plugin_id}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error initializing plugins: {str(e)}")

    def show(self):  # <--- ADD THIS METHOD
        if self.main_window:
            self.main_window.show()
        else:
            self.logger.error("Main window not initialized, cannot show.")

    def cleanup(self):
        """Clean up the application."""
        self.logger.info("Cleaning up NebulaFusion browser...")

        # Emit closing signal
        self.closing.emit()

        # Trigger hook
        self.hook_registry.trigger_hook("onBrowserExit")

        # Clean up managers
        self.theme_manager.cleanup()
        self.plugin_manager.cleanup()
        self.plugin_loader.cleanup()
        self.hook_registry.cleanup()
        self.content_security_manager.cleanup()
        self.security_manager.cleanup()
        self.download_manager.cleanup()
        self.cookies_manager.cleanup()
        self.bookmarks_manager.cleanup()
        self.history_manager.cleanup()
        self.tab_manager.cleanup()
        self.web_engine_manager.cleanup()
        self.settings_manager.cleanup()

        self.logger.info("NebulaFusion browser cleaned up.")

        return True

    def get_version(self):
        """Get the application version."""
        return "1.0.0"

    def get_name(self):
        """Get the application name."""
        return "NebulaFusion"

    def get_description(self):
        """Get the application description."""
        return "A modern web browser with a robust plugin system."

    def get_author(self):
        """Get the application author."""
        return "NebulaFusion Team"

    def get_website(self):
        """Get the application website."""
        return "https://nebulafusion.example.com"

    def get_license(self):
        """Get the application license."""
        return "MIT"


# SettingsManager class remains unchanged from your provided file, it seems correct.
class SettingsManager(QObject):
    """
    Manager for application settings.
    Handles loading, saving, and accessing settings.
    """

    # Signals
    setting_changed = pyqtSignal(str, object)  # key, value

    def __init__(self, app_controller):
        """Initialize the settings manager."""
        super().__init__()
        self.app_controller = app_controller

        # Settings
        self.settings = QSettings("NebulaFusion", "Browser")

        # Default settings
        self.default_settings = {
            "general.homepage": "https://www.google.com",
            "general.search_engine": "https://www.google.com/search?q=",
            "general.new_tab_page": "about:newtab",
            "general.download_directory": os.path.expanduser("~/Downloads"),
            "general.startup_mode": "restore",  # restore, homepage, blank
            "general.language": "en-US",
            "privacy.do_not_track": True,
            "privacy.block_third_party_cookies": False,
            "privacy.clear_history_on_exit": False,
            "privacy.clear_cookies_on_exit": False,
            "privacy.clear_cache_on_exit": False,
            "appearance.theme": "Default",
            "appearance.show_bookmarks_bar": True,
            "appearance.show_status_bar": True,
            "appearance.show_home_button": True,
            "tabs.close_button_on_tabs": True,
            "tabs.confirm_close_multiple_tabs": True,
            "tabs.switch_to_new_tabs": True,
            "advanced.hardware_acceleration": True,
            "advanced.javascript_enabled": True,
            "advanced.plugins_enabled": True,
            "advanced.developer_tools_enabled": True,
        }

        # Initialize settings
        self.initialized = (
            False  # This is specific to SettingsManager, no conflict here
        )

    def initialize(self):
        """Initialize the settings manager."""
        self.app_controller.logger.info("Initializing settings manager...")

        # Load settings
        self._load_settings()

        # Update state
        self.initialized = True

        self.app_controller.logger.info("Settings manager initialized.")

        return True

    def cleanup(self):
        """Clean up the settings manager."""
        self.app_controller.logger.info("Cleaning up settings manager...")

        # Save settings
        self._save_settings()

        # Update state
        self.initialized = False

        self.app_controller.logger.info("Settings manager cleaned up.")

        return True

    def _load_settings(self):
        """Load settings."""
        # Load settings from QSettings
        for key, default_value in self.default_settings.items():
            value = self.settings.value(key, default_value)

            # Convert value to correct type
            if isinstance(default_value, bool):
                if isinstance(value, str):
                    value = value.lower() in ["true", "1", "yes"]
                else:
                    value = bool(value)
            elif isinstance(default_value, int):
                value = int(value)
            elif isinstance(default_value, float):
                value = float(value)

            # Set setting
            self.set_setting(key, value, emit_signal=False)

    def _save_settings(self):
        """Save settings."""
        # Save settings to QSettings
        for key, value in self.default_settings.items():
            self.settings.setValue(key, value)
        # Ensure the settings are written to disk
        self.settings.sync()

    def get_setting(self, key, default=None):
        """Get a setting."""
        # Check if key exists
        if key in self.default_settings:
            return self.default_settings[key]

        # Return default value
        return default

    def set_setting(self, key, value, emit_signal=True):
        """Set a setting."""
        # Set setting
        self.default_settings[key] = value

        # Save setting
        self.settings.setValue(key, value)

        # Emit signal
        if emit_signal:
            self.setting_changed.emit(key, value)

        return True

    def reset_setting(self, key):
        """Reset a setting to its default value."""
        # Check if key exists
        if key in self.default_settings:
            # Get default value
            default_value = self.default_settings[key]

            # Set setting
            self.set_setting(key, default_value)

            return True

        return False

    def reset_all_settings(self):
        """Reset all settings to their default values."""
        # Reset all settings
        for key in self.default_settings:
            self.reset_setting(key)

        return True
