#!/usr/bin/env python3
# NebulaFusion Browser - Settings Dialog

import os
import sys
from PyQt6.QtWidgets import (
    QDialog,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QFormLayout,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon


class SettingsDialog(QDialog):
    """
    Settings dialog for browser configuration.
    """

    def __init__(self, app_controller):
        """Initialize the settings dialog."""
        super().__init__()
        self.app_controller = app_controller

        # Set properties
        self.setWindowTitle("NebulaFusion Settings")
        self.setMinimumSize(600, 500)

        # Create layout
        self.layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_general_tab()
        self._create_privacy_tab()
        self._create_security_tab()
        self._create_downloads_tab()
        self._create_appearance_tab()
        self._create_advanced_tab()
        self._create_unique_features_tab()

        # Create buttons
        self._create_buttons()

        # Load settings
        self._load_settings()

    def _create_general_tab(self):
        """Create general settings tab."""
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QFormLayout(startup_group)

        # Home page
        self.home_page_edit = QLineEdit()
        startup_layout.addRow("Home page:", self.home_page_edit)

        # Restore session
        self.restore_session_check = QCheckBox("Restore previous session on startup")
        startup_layout.addRow("", self.restore_session_check)

        general_layout.addWidget(startup_group)

        # Search group
        search_group = QGroupBox("Search")
        search_layout = QFormLayout(search_group)

        # Default search engine
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["Google", "Bing", "DuckDuckGo"])
        search_layout.addRow("Default search engine:", self.search_engine_combo)

        general_layout.addWidget(search_group)

        # Features group
        features_group = QGroupBox("Features")
        features_layout = QFormLayout(features_group)

        # JavaScript
        self.javascript_check = QCheckBox("Enable JavaScript")
        features_layout.addRow("", self.javascript_check)

        # Plugins
        self.plugins_check = QCheckBox("Enable plugins")
        features_layout.addRow("", self.plugins_check)

        general_layout.addWidget(features_group)

        # Add tab
        self.tab_widget.addTab(general_tab, "General")

    def _create_privacy_tab(self):
        """Create privacy settings tab."""
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)

        # Browsing history group
        history_group = QGroupBox("Browsing History")
        history_layout = QFormLayout(history_group)

        # Clear history on exit
        self.clear_history_check = QCheckBox("Clear history when browser closes")
        history_layout.addRow("", self.clear_history_check)

        # Clear history button
        self.clear_history_button = QPushButton("Clear Browsing History...")
        self.clear_history_button.clicked.connect(self._on_clear_history)
        history_layout.addRow("", self.clear_history_button)

        privacy_layout.addWidget(history_group)

        # Cookies group
        cookies_group = QGroupBox("Cookies")
        cookies_layout = QFormLayout(cookies_group)

        # Enable cookies
        self.cookies_check = QCheckBox("Enable cookies")
        cookies_layout.addRow("", self.cookies_check)

        # Block third-party cookies
        self.third_party_cookies_check = QCheckBox("Block third-party cookies")
        cookies_layout.addRow("", self.third_party_cookies_check)

        # Clear cookies on exit
        self.clear_cookies_check = QCheckBox("Clear cookies when browser closes")
        cookies_layout.addRow("", self.clear_cookies_check)

        # Clear cookies button
        self.clear_cookies_button = QPushButton("Clear Cookies...")
        self.clear_cookies_button.clicked.connect(self._on_clear_cookies)
        cookies_layout.addRow("", self.clear_cookies_button)

        privacy_layout.addWidget(cookies_group)

        # Tracking group
        tracking_group = QGroupBox("Tracking")
        tracking_layout = QFormLayout(tracking_group)

        # Do not track
        self.do_not_track_check = QCheckBox(
            'Send "Do Not Track" request with browsing traffic'
        )
        tracking_layout.addRow("", self.do_not_track_check)

        # Block trackers
        self.block_trackers_check = QCheckBox("Block known trackers")
        tracking_layout.addRow("", self.block_trackers_check)

        privacy_layout.addWidget(tracking_group)

        # Add tab
        self.tab_widget.addTab(privacy_tab, "Privacy")

    def _create_security_tab(self):
        """Create security settings tab."""
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)

        # Protection group
        protection_group = QGroupBox("Protection")
        protection_layout = QFormLayout(protection_group)

        # Block malicious sites
        self.block_malicious_check = QCheckBox("Block dangerous and deceptive sites")
        protection_layout.addRow("", self.block_malicious_check)

        # Warn on insecure forms
        self.warn_insecure_forms_check = QCheckBox(
            "Warn about password entry on non-secure pages"
        )
        protection_layout.addRow("", self.warn_insecure_forms_check)

        # Phishing protection
        self.phishing_protection_check = QCheckBox("Enable phishing protection")
        protection_layout.addRow("", self.phishing_protection_check)

        # XSS protection
        self.xss_protection_check = QCheckBox(
            "Enable cross-site scripting (XSS) protection"
        )
        protection_layout.addRow("", self.xss_protection_check)

        # Content verification
        self.content_verification_check = QCheckBox(
            "Verify content integrity when possible"
        )
        protection_layout.addRow("", self.content_verification_check)

        security_layout.addWidget(protection_group)

        # Plugin security group
        plugin_security_group = QGroupBox("Plugin Security")
        plugin_security_layout = QFormLayout(plugin_security_group)

        # Plugin sandboxing
        self.plugin_sandbox_check = QCheckBox("Enable plugin sandboxing")
        plugin_security_layout.addRow("", self.plugin_sandbox_check)

        # Plugin CPU limit
        self.plugin_cpu_spin = QSpinBox()
        self.plugin_cpu_spin.setRange(1, 100)
        self.plugin_cpu_spin.setSuffix("%")
        plugin_security_layout.addRow("Plugin CPU limit:", self.plugin_cpu_spin)

        # Plugin memory limit
        self.plugin_memory_spin = QSpinBox()
        self.plugin_memory_spin.setRange(10, 1000)
        self.plugin_memory_spin.setSuffix(" MB")
        plugin_security_layout.addRow("Plugin memory limit:", self.plugin_memory_spin)

        # Plugin network limit
        self.plugin_network_spin = QSpinBox()
        self.plugin_network_spin.setRange(10, 1000)
        self.plugin_network_spin.setSuffix(" requests/min")
        plugin_security_layout.addRow("Plugin network limit:", self.plugin_network_spin)

        security_layout.addWidget(plugin_security_group)

        # Add tab
        self.tab_widget.addTab(security_tab, "Security")

    def _create_downloads_tab(self):
        """Create downloads settings tab."""
        downloads_tab = QWidget()
        downloads_layout = QVBoxLayout(downloads_tab)

        # Downloads group
        downloads_group = QGroupBox("Downloads")
        downloads_layout_group = QFormLayout(downloads_group)

        # Download location
        self.download_location_edit = QLineEdit()
        self.download_location_button = QPushButton("Browse...")
        self.download_location_button.clicked.connect(self._on_browse_download_location)

        download_location_layout = QHBoxLayout()
        download_location_layout.addWidget(self.download_location_edit)
        download_location_layout.addWidget(self.download_location_button)

        downloads_layout_group.addRow("Download location:", download_location_layout)

        # Ask before download
        self.ask_download_check = QCheckBox(
            "Ask where to save each file before downloading"
        )
        downloads_layout_group.addRow("", self.ask_download_check)

        # Open after download
        self.open_download_check = QCheckBox("Open files after downloading")
        downloads_layout_group.addRow("", self.open_download_check)

        downloads_layout.addWidget(downloads_group)

        # Add tab
        self.tab_widget.addTab(downloads_tab, "Downloads")

    def _create_appearance_tab(self):
        """Create appearance settings tab."""
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)

        # Theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)

        # Theme selection
        self.theme_combo = QComboBox()
        for theme_name in self.app_controller.theme_manager.available_themes:
            self.theme_combo.addItem(theme_name.capitalize(), theme_name)

        theme_layout.addRow("Theme:", self.theme_combo)

        appearance_layout.addWidget(theme_group)

        # UI elements group
        ui_group = QGroupBox("UI Elements")
        ui_layout = QFormLayout(ui_group)

        # Show bookmarks bar
        self.bookmarks_bar_check = QCheckBox("Show bookmarks bar")
        ui_layout.addRow("", self.bookmarks_bar_check)

        # Show status bar
        self.status_bar_check = QCheckBox("Show status bar")
        ui_layout.addRow("", self.status_bar_check)

        # Show tab previews
        self.tab_previews_check = QCheckBox("Show tab previews on hover")
        ui_layout.addRow("", self.tab_previews_check)

        # Tab position
        self.tab_position_combo = QComboBox()
        self.tab_position_combo.addItems(["Top", "Bottom", "Left", "Right"])
        ui_layout.addRow("Tab position:", self.tab_position_combo)

        # Toolbar style
        self.toolbar_style_combo = QComboBox()
        self.toolbar_style_combo.addItems(["Icon Only", "Text Only", "Icon and Text"])
        ui_layout.addRow("Toolbar style:", self.toolbar_style_combo)

        appearance_layout.addWidget(ui_group)

        # Add tab
        self.tab_widget.addTab(appearance_tab, "Appearance")

    def _create_advanced_tab(self):
        """Create advanced settings tab."""
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Cache group
        cache_group = QGroupBox("Cache")
        cache_layout = QFormLayout(cache_group)

        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("Cache size:", self.cache_size_spin)

        # Clear cache button
        self.clear_cache_button = QPushButton("Clear Cache...")
        self.clear_cache_button.clicked.connect(self._on_clear_cache)
        cache_layout.addRow("", self.clear_cache_button)

        advanced_layout.addWidget(cache_group)

        # Plugins group
        plugins_group = QGroupBox("Plugins")
        plugins_layout = QFormLayout(plugins_group)

        # Plugin directory
        self.plugin_directory_edit = QLineEdit()
        self.plugin_directory_button = QPushButton("Browse...")
        self.plugin_directory_button.clicked.connect(self._on_browse_plugin_directory)

        plugin_directory_layout = QHBoxLayout()
        plugin_directory_layout.addWidget(self.plugin_directory_edit)
        plugin_directory_layout.addWidget(self.plugin_directory_button)

        plugins_layout.addRow("Plugin directory:", plugin_directory_layout)

        advanced_layout.addWidget(plugins_group)

        # Developer group
        developer_group = QGroupBox("Developer")
        developer_layout = QFormLayout(developer_group)

        # Developer tools
        self.developer_tools_check = QCheckBox("Enable developer tools")
        developer_layout.addRow("", self.developer_tools_check)

        # Experimental features
        self.experimental_features_check = QCheckBox("Enable experimental features")
        developer_layout.addRow("", self.experimental_features_check)

        # Log level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["Debug", "Info", "Warning", "Error"])
        developer_layout.addRow("Log level:", self.log_level_combo)

        advanced_layout.addWidget(developer_group)

        # Add tab
        self.tab_widget.addTab(advanced_tab, "Advanced")

    def _create_unique_features_tab(self):
        """Create unique features settings tab."""
        unique_tab = QWidget()
        unique_layout = QVBoxLayout(unique_tab)

        # Reality Augmentation group
        reality_group = QGroupBox("Reality Augmentation")
        reality_layout = QFormLayout(reality_group)

        # Enable Reality Augmentation
        self.reality_augmentation_check = QCheckBox("Enable Reality Augmentation")
        reality_layout.addRow("", self.reality_augmentation_check)

        unique_layout.addWidget(reality_group)

        # Collaborative Browsing group
        collaborative_group = QGroupBox("Collaborative Browsing")
        collaborative_layout = QFormLayout(collaborative_group)

        # Enable Collaborative Browsing
        self.collaborative_browsing_check = QCheckBox("Enable Collaborative Browsing")
        collaborative_layout.addRow("", self.collaborative_browsing_check)

        unique_layout.addWidget(collaborative_group)

        # Content Transformation group
        transform_group = QGroupBox("Content Transformation")
        transform_layout = QFormLayout(transform_group)

        # Enable Content Transformation
        self.content_transformation_check = QCheckBox("Enable Content Transformation")
        transform_layout.addRow("", self.content_transformation_check)

        unique_layout.addWidget(transform_group)

        # Time-Travel Browsing group
        time_travel_group = QGroupBox("Time-Travel Browsing")
        time_travel_layout = QFormLayout(time_travel_group)

        # Enable Time-Travel Browsing
        self.time_travel_check = QCheckBox("Enable Time-Travel Browsing")
        time_travel_layout.addRow("", self.time_travel_check)

        unique_layout.addWidget(time_travel_group)

        # Dimensional Tabs group
        dimensional_group = QGroupBox("Dimensional Tabs")
        dimensional_layout = QFormLayout(dimensional_group)

        # Enable Dimensional Tabs
        self.dimensional_tabs_check = QCheckBox("Enable Dimensional Tabs")
        dimensional_layout.addRow("", self.dimensional_tabs_check)

        unique_layout.addWidget(dimensional_group)

        # Voice Commands group
        voice_group = QGroupBox("Voice Commands")
        voice_layout = QFormLayout(voice_group)

        # Enable Voice Commands
        self.voice_commands_check = QCheckBox("Enable Voice Commands")
        voice_layout.addRow("", self.voice_commands_check)

        unique_layout.addWidget(voice_group)

        # Add tab
        self.tab_widget.addTab(unique_tab, "Unique Features")

    def _create_buttons(self):
        """Create dialog buttons."""
        button_layout = QHBoxLayout()

        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_button)

        # Spacer
        button_layout.addStretch()

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        self.layout.addLayout(button_layout)

    def _load_settings(self):
        """Load settings from settings manager."""
        settings = self.app_controller.settings_manager.default_settings

        # General settings
        self.home_page_edit.setText(settings.get("home_page", ""))
        self.restore_session_check.setChecked(settings.get("restore_session", True))

        search_engine = settings.get("default_search_engine", "google")
        if search_engine == "google":
            self.search_engine_combo.setCurrentIndex(0)
        elif search_engine == "bing":
            self.search_engine_combo.setCurrentIndex(1)
        elif search_engine == "duckduckgo":
            self.search_engine_combo.setCurrentIndex(2)

        self.javascript_check.setChecked(settings.get("enable_javascript", True))
        self.plugins_check.setChecked(settings.get("enable_plugins", True))

        # Privacy settings
        self.clear_history_check.setChecked(
            settings.get("clear_history_on_exit", False)
        )
        self.cookies_check.setChecked(settings.get("enable_cookies", True))
        self.third_party_cookies_check.setChecked(
            settings.get("block_third_party_cookies", False)
        )
        self.clear_cookies_check.setChecked(
            settings.get("clear_cookies_on_exit", False)
        )
        self.do_not_track_check.setChecked(settings.get("do_not_track", False))
        self.block_trackers_check.setChecked(settings.get("block_trackers", False))

        # Security settings
        self.block_malicious_check.setChecked(
            settings.get("security_block_malicious_sites", True)
        )
        self.warn_insecure_forms_check.setChecked(
            settings.get("security_warn_on_insecure_forms", True)
        )
        self.phishing_protection_check.setChecked(
            settings.get("security_enable_phishing_protection", True)
        )
        self.xss_protection_check.setChecked(
            settings.get("security_enable_xss_protection", True)
        )
        self.content_verification_check.setChecked(
            settings.get("security_enable_content_verification", True)
        )
        self.plugin_sandbox_check.setChecked(
            settings.get("security_plugin_sandbox_enabled", True)
        )
        self.plugin_cpu_spin.setValue(settings.get("security_plugin_cpu_percent", 10))
        self.plugin_memory_spin.setValue(settings.get("security_plugin_memory_mb", 100))
        self.plugin_network_spin.setValue(
            settings.get("security_plugin_network_requests_per_minute", 60)
        )

        # Downloads settings
        self.download_location_edit.setText(settings.get("download_directory", ""))
        self.ask_download_check.setChecked(settings.get("ask_before_download", True))
        self.open_download_check.setChecked(settings.get("open_after_download", False))

        # Appearance settings
        theme = settings.get("theme", "default")
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == theme:
                self.theme_combo.setCurrentIndex(i)
                break

        self.bookmarks_bar_check.setChecked(settings.get("show_bookmarks_bar", True))
        self.status_bar_check.setChecked(settings.get("show_status_bar", True))
        self.tab_previews_check.setChecked(settings.get("show_tab_previews", True))

        tab_position = settings.get("tab_position", "top")
        if tab_position == "top":
            self.tab_position_combo.setCurrentIndex(0)
        elif tab_position == "bottom":
            self.tab_position_combo.setCurrentIndex(1)
        elif tab_position == "left":
            self.tab_position_combo.setCurrentIndex(2)
        elif tab_position == "right":
            self.tab_position_combo.setCurrentIndex(3)

        toolbar_style = settings.get("toolbar_style", "icon_text")
        if toolbar_style == "icon":
            self.toolbar_style_combo.setCurrentIndex(0)
        elif toolbar_style == "text":
            self.toolbar_style_combo.setCurrentIndex(1)
        elif toolbar_style == "icon_text":
            self.toolbar_style_combo.setCurrentIndex(2)

        # Advanced settings
        self.cache_size_spin.setValue(settings.get("cache_size_mb", 100))
        self.plugin_directory_edit.setText(settings.get("plugin_directory", ""))
        self.developer_tools_check.setChecked(
            settings.get("enable_developer_tools", False)
        )
        self.experimental_features_check.setChecked(
            settings.get("enable_experimental_features", False)
        )

        log_level = settings.get("log_level", "info")
        if log_level == "debug":
            self.log_level_combo.setCurrentIndex(0)
        elif log_level == "info":
            self.log_level_combo.setCurrentIndex(1)
        elif log_level == "warning":
            self.log_level_combo.setCurrentIndex(2)
        elif log_level == "error":
            self.log_level_combo.setCurrentIndex(3)

        # Unique features settings
        self.reality_augmentation_check.setChecked(
            settings.get("enable_reality_augmentation", True)
        )
        self.collaborative_browsing_check.setChecked(
            settings.get("enable_collaborative_browsing", True)
        )
        self.content_transformation_check.setChecked(
            settings.get("enable_content_transformation", True)
        )
        self.time_travel_check.setChecked(settings.get("enable_time_travel", True))
        self.dimensional_tabs_check.setChecked(
            settings.get("enable_dimensional_tabs", True)
        )
        self.voice_commands_check.setChecked(
            settings.get("enable_voice_commands", True)
        )

    def _save_settings(self):
        """Save settings to settings manager."""
        # General settings
        self.app_controller.settings_manager.set_setting(
            "home_page", self.home_page_edit.text()
        )
        self.app_controller.settings_manager.set_setting(
            "restore_session", self.restore_session_check.isChecked()
        )

        search_engine_index = self.search_engine_combo.currentIndex()
        if search_engine_index == 0:
            self.app_controller.settings_manager.set_setting(
                "default_search_engine", "google"
            )
        elif search_engine_index == 1:
            self.app_controller.settings_manager.set_setting(
                "default_search_engine", "bing"
            )
        elif search_engine_index == 2:
            self.app_controller.settings_manager.set_setting(
                "default_search_engine", "duckduckgo"
            )

        self.app_controller.settings_manager.set_setting(
            "enable_javascript", self.javascript_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_plugins", self.plugins_check.isChecked()
        )

        # Privacy settings
        self.app_controller.settings_manager.set_setting(
            "clear_history_on_exit", self.clear_history_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_cookies", self.cookies_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "block_third_party_cookies", self.third_party_cookies_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "clear_cookies_on_exit", self.clear_cookies_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "do_not_track", self.do_not_track_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "block_trackers", self.block_trackers_check.isChecked()
        )

        # Security settings
        self.app_controller.settings_manager.set_setting(
            "security_block_malicious_sites", self.block_malicious_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "security_warn_on_insecure_forms",
            self.warn_insecure_forms_check.isChecked(),
        )
        self.app_controller.settings_manager.set_setting(
            "security_enable_phishing_protection",
            self.phishing_protection_check.isChecked(),
        )
        self.app_controller.settings_manager.set_setting(
            "security_enable_xss_protection", self.xss_protection_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "security_enable_content_verification",
            self.content_verification_check.isChecked(),
        )
        self.app_controller.settings_manager.set_setting(
            "security_plugin_sandbox_enabled", self.plugin_sandbox_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "security_plugin_cpu_percent", self.plugin_cpu_spin.value()
        )
        self.app_controller.settings_manager.set_setting(
            "security_plugin_memory_mb", self.plugin_memory_spin.value()
        )
        self.app_controller.settings_manager.set_setting(
            "security_plugin_network_requests_per_minute",
            self.plugin_network_spin.value(),
        )

        # Downloads settings
        self.app_controller.settings_manager.set_setting(
            "download_directory", self.download_location_edit.text()
        )
        self.app_controller.settings_manager.set_setting(
            "ask_before_download", self.ask_download_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "open_after_download", self.open_download_check.isChecked()
        )

        # Appearance settings
        theme_index = self.theme_combo.currentIndex()
        if theme_index >= 0:
            self.app_controller.settings_manager.set_setting(
                "theme", self.theme_combo.itemData(theme_index)
            )

        self.app_controller.settings_manager.set_setting(
            "show_bookmarks_bar", self.bookmarks_bar_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "show_status_bar", self.status_bar_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "show_tab_previews", self.tab_previews_check.isChecked()
        )

        tab_position_index = self.tab_position_combo.currentIndex()
        if tab_position_index == 0:
            self.app_controller.settings_manager.set_setting("tab_position", "top")
        elif tab_position_index == 1:
            self.app_controller.settings_manager.set_setting("tab_position", "bottom")
        elif tab_position_index == 2:
            self.app_controller.settings_manager.set_setting("tab_position", "left")
        elif tab_position_index == 3:
            self.app_controller.settings_manager.set_setting("tab_position", "right")

        toolbar_style_index = self.toolbar_style_combo.currentIndex()
        if toolbar_style_index == 0:
            self.app_controller.settings_manager.set_setting("toolbar_style", "icon")
        elif toolbar_style_index == 1:
            self.app_controller.settings_manager.set_setting("toolbar_style", "text")
        elif toolbar_style_index == 2:
            self.app_controller.settings_manager.set_setting(
                "toolbar_style", "icon_text"
            )

        # Advanced settings
        self.app_controller.settings_manager.set_setting(
            "cache_size_mb", self.cache_size_spin.value()
        )
        self.app_controller.settings_manager.set_setting(
            "plugin_directory", self.plugin_directory_edit.text()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_developer_tools", self.developer_tools_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_experimental_features", self.experimental_features_check.isChecked()
        )

        log_level_index = self.log_level_combo.currentIndex()
        if log_level_index == 0:
            self.app_controller.settings_manager.set_setting("log_level", "debug")
        elif log_level_index == 1:
            self.app_controller.settings_manager.set_setting("log_level", "info")
        elif log_level_index == 2:
            self.app_controller.settings_manager.set_setting("log_level", "warning")
        elif log_level_index == 3:
            self.app_controller.settings_manager.set_setting("log_level", "error")

        # Unique features settings
        self.app_controller.settings_manager.set_setting(
            "enable_reality_augmentation", self.reality_augmentation_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_collaborative_browsing",
            self.collaborative_browsing_check.isChecked(),
        )
        self.app_controller.settings_manager.set_setting(
            "enable_content_transformation",
            self.content_transformation_check.isChecked(),
        )
        self.app_controller.settings_manager.set_setting(
            "enable_time_travel", self.time_travel_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_dimensional_tabs", self.dimensional_tabs_check.isChecked()
        )
        self.app_controller.settings_manager.set_setting(
            "enable_voice_commands", self.voice_commands_check.isChecked()
        )

    def _on_browse_download_location(self):
        """Handle browse download location button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Location", self.download_location_edit.text()
        )

        if directory:
            self.download_location_edit.setText(directory)

    def _on_browse_plugin_directory(self):
        """Handle browse plugin directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Plugin Directory", self.plugin_directory_edit.text()
        )

        if directory:
            self.plugin_directory_edit.setText(directory)

    def _on_clear_history(self):
        """Handle clear history button click."""
        self.app_controller.history_manager.clear_history()

    def _on_clear_cookies(self):
        """Handle clear cookies button click."""
        self.app_controller.cookies_manager.clear_cookies()

    def _on_clear_cache(self):
        """Handle clear cache button click."""
        self.app_controller.web_engine_manager.clear_cache()

    def _on_reset(self):
        """Handle reset button click."""
        self.app_controller.settings_manager.reset_all_settings()
        self._load_settings()

    def _on_save(self):
        """Handle save button click."""
        self._save_settings()
        self.accept()
