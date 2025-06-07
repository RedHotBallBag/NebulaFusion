#!/usr/bin/env python3
# NebulaFusion Browser - Settings Manager

import os
import sys
import json
import time
from PyQt6.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    """
    Manages browser settings and configuration.
    """

    # Signals
    setting_changed = pyqtSignal(str, object)
    settings_loaded = pyqtSignal()
    settings_saved = pyqtSignal()

    def __init__(self, app_controller):
        """Initialize the settings manager."""
        super().__init__()
        self.app_controller = app_controller

        # Settings file
        self.settings_file = os.path.expanduser("~/.nebulafusion/settings.json")

        # Settings
        self.settings = {}

        # Default settings
        self.default_settings = {
            # Browser settings
            "browser_version": "1.0.0",
            "home_page": "https://www.google.com",
            "restore_session": True,
            "default_search_engine": "google",
            "enable_javascript": True,
            "enable_plugins": True,
            "enable_cookies": True,
            "enable_history": True,
            "enable_bookmarks": True,
            "enable_downloads": True,
            "enable_private_browsing": True,
            "enable_reality_augmentation": True,
            "enable_collaborative_browsing": True,
            "enable_content_transformation": True,
            "enable_time_travel": True,
            "enable_dimensional_tabs": True,
            "enable_voice_commands": True,
            # UI settings
            "theme": "default",
            "show_bookmarks_bar": True,
            "show_status_bar": True,
            "show_tab_previews": True,
            "tab_position": "top",
            "toolbar_style": "icon_text",
            # Privacy settings
            "clear_history_on_exit": False,
            "clear_cookies_on_exit": False,
            "do_not_track": False,
            "block_third_party_cookies": False,
            "block_popups": True,
            "block_ads": False,
            "block_trackers": False,
            # Security settings
            "security_block_malicious_sites": True,
            "security_warn_on_insecure_forms": True,
            "security_enable_phishing_protection": True,
            "security_enable_xss_protection": True,
            "security_enable_content_verification": True,
            "security_plugin_sandbox_enabled": True,
            "security_plugin_cpu_percent": 10,
            "security_plugin_memory_mb": 100,
            "security_plugin_network_requests_per_minute": 60,
            "security_plugin_file_access_paths": ["~/.nebulafusion/plugins"],
            # Download settings
            "download_directory": os.path.expanduser("~/Downloads"),
            "ask_before_download": True,
            "open_after_download": False,
            # Advanced settings
            "cache_size_mb": 100,
            "max_tabs": 50,
            "plugin_directory": os.path.expanduser("~/.nebulafusion/plugins"),
            "theme_directory": os.path.expanduser("~/.nebulafusion/themes"),
            "log_level": "info",
            "enable_developer_tools": False,
            "enable_experimental_features": False,
        }

    def initialize(self):
        """Initialize the settings manager."""
        # Create settings directory if it doesn't exist
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

        # Load settings
        self.load_settings()

    def load_settings(self):
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r") as f:
                    self.settings = json.load(f)
            else:
                # Create default settings
                self.settings = self.default_settings.copy()

                # Save settings
                self.save_settings()

            # Emit signal
            self.settings_loaded.emit()

        except Exception as e:
            self.app_controller.logger.error(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()

    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)

            # Emit signal
            self.settings_saved.emit()

        except Exception as e:
            self.app_controller.logger.error(f"Error saving settings: {e}")

    def get_setting(self, key, default=None):
        """Get a setting."""
        return self.settings.get(
            key, default if default is not None else self.default_settings.get(key)
        )

    def set_setting(self, key, value):
        """Set a setting."""
        # Check if value is different
        if key in self.settings and self.settings[key] == value:
            return

        # Update setting
        self.settings[key] = value

        # Save settings
        self.save_settings()

        # Emit signal
        self.setting_changed.emit(key, value)

    def reset_setting(self, key):
        """Reset a setting to default."""
        if key in self.default_settings:
            self.set_setting(key, self.default_settings[key])

    def reset_all_settings(self):
        """Reset all settings to defaults."""
        self.settings = self.default_settings.copy()
        self.save_settings()

        # Emit signals for all settings
        for key, value in self.settings.items():
            self.setting_changed.emit(key, value)

    def get_all_settings(self):
        """Get all settings."""
        return self.settings

    def get_default_settings(self):
        """Get default settings."""
        return self.default_settings

    def import_settings(self, settings_file):
        """Import settings from a file."""
        try:
            with open(settings_file, "r") as f:
                imported_settings = json.load(f)

            # Update settings
            self.settings.update(imported_settings)

            # Save settings
            self.save_settings()

            # Emit signals for all settings
            for key, value in imported_settings.items():
                self.setting_changed.emit(key, value)

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error importing settings: {e}")
            return False

    def export_settings(self, settings_file):
        """Export settings to a file."""
        try:
            with open(settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error exporting settings: {e}")
            return False

    def get_settings_by_category(self, category):
        """Get settings by category."""
        if category == "browser":
            return {
                k: v
                for k, v in self.settings.items()
                if k.startswith("browser_")
                or k
                in [
                    "home_page",
                    "restore_session",
                    "default_search_engine",
                    "enable_javascript",
                    "enable_plugins",
                    "enable_cookies",
                    "enable_history",
                    "enable_bookmarks",
                    "enable_downloads",
                    "enable_private_browsing",
                    "enable_reality_augmentation",
                    "enable_collaborative_browsing",
                    "enable_content_transformation",
                    "enable_time_travel",
                    "enable_dimensional_tabs",
                    "enable_voice_commands",
                ]
            }

        elif category == "ui":
            return {
                k: v
                for k, v in self.settings.items()
                if k.startswith("ui_")
                or k
                in [
                    "theme",
                    "show_bookmarks_bar",
                    "show_status_bar",
                    "show_tab_previews",
                    "tab_position",
                    "toolbar_style",
                ]
            }

        elif category == "privacy":
            return {
                k: v
                for k, v in self.settings.items()
                if k.startswith("privacy_")
                or k
                in [
                    "clear_history_on_exit",
                    "clear_cookies_on_exit",
                    "do_not_track",
                    "block_third_party_cookies",
                    "block_popups",
                    "block_ads",
                    "block_trackers",
                ]
            }

        elif category == "security":
            return {k: v for k, v in self.settings.items() if k.startswith("security_")}

        elif category == "download":
            return {k: v for k, v in self.settings.items() if k.startswith("download_")}

        elif category == "advanced":
            return {
                k: v
                for k, v in self.settings.items()
                if k.startswith("advanced_")
                or k
                in [
                    "cache_size_mb",
                    "max_tabs",
                    "plugin_directory",
                    "theme_directory",
                    "log_level",
                    "enable_developer_tools",
                    "enable_experimental_features",
                ]
            }

        else:
            return {}
