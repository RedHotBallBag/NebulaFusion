#!/usr/bin/env python3
# NebulaFusion Browser - Theme Manager

import os
import sys
import json
from PyQt6.QtCore import QObject, pyqtSignal, QFile, QTextStream
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    """
    Manager for browser themes.
    Handles loading, applying, and switching themes.
    """

    # Signals
    theme_changed = pyqtSignal(str)  # theme_name
    theme_loaded = pyqtSignal(str)  # theme_name

    def __init__(self, app_controller):
        """Initialize the theme manager."""
        super().__init__()
        self.app_controller = app_controller

        # Current theme
        self.current_theme = None

        # Available themes
        self.available_themes = {}

        # Theme directories
        self.theme_dirs = []

        # Default theme directory
        self.default_theme_dir = os.path.expanduser("~/.nebulafusion/themes")

        # Built-in theme directory
        self.builtin_theme_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "themes",
            "default_themes",
        )

    def initialize(self):
        """Initialize the theme manager."""
        self.app_controller.logger.info("Initializing theme manager...")

        # Create default theme directory if it doesn't exist
        os.makedirs(self.default_theme_dir, exist_ok=True)

        # Add theme directories
        self.theme_dirs.append(self.default_theme_dir)
        if os.path.exists(self.builtin_theme_dir):
            self.theme_dirs.append(self.builtin_theme_dir)

        # Load themes
        self._load_themes()

        # Apply default theme
        default_theme = self.app_controller.settings_manager.get_setting(
            "appearance.theme", "Default"
        )
        self.apply_theme(default_theme)

        self.app_controller.logger.info("Theme manager initialized.")

    def _load_themes(self):
        """Load themes from theme directories."""
        # Clear available themes
        self.available_themes = {}

        # Load built-in themes
        self._load_builtin_themes()

        # Load themes from theme directories
        for theme_dir in self.theme_dirs:
            # Check if directory exists
            if not os.path.exists(theme_dir):
                continue

            # Get theme files
            for item in os.listdir(theme_dir):
                item_path = os.path.join(theme_dir, item)

                # Check if item is a directory
                if os.path.isdir(item_path):
                    # Check if directory contains theme.json
                    theme_json_path = os.path.join(item_path, "theme.json")
                    if os.path.exists(theme_json_path):
                        # Load theme
                        self._load_theme(item_path)

    def _load_builtin_themes(self):
        """Load built-in themes."""
        # Default theme
        self.available_themes["Default"] = {
            "name": "Default",
            "description": "Default theme for NebulaFusion browser.",
            "author": "NebulaFusion Team",
            "version": "1.0.0",
            "dark": False,
            "stylesheet": self._get_default_stylesheet(),
            "colors": {
                "primary": "#4285F4",
                "secondary": "#34A853",
                "accent": "#FBBC05",
                "background": "#FFFFFF",
                "foreground": "#202124",
                "surface": "#F8F9FA",
                "error": "#EA4335",
                "warning": "#FBBC05",
                "success": "#34A853",
                "info": "#4285F4",
            },
        }

        # Dark theme
        self.available_themes["Dark"] = {
            "name": "Dark",
            "description": "Dark theme for NebulaFusion browser.",
            "author": "NebulaFusion Team",
            "version": "1.0.0",
            "dark": True,
            "stylesheet": self._get_dark_stylesheet(),
            "colors": {
                "primary": "#BB86FC",
                "secondary": "#03DAC6",
                "accent": "#CF6679",
                "background": "#121212",
                "foreground": "#E1E1E1",
                "surface": "#1E1E1E",
                "error": "#CF6679",
                "warning": "#FFDE03",
                "success": "#03DAC6",
                "info": "#BB86FC",
            },
        }

        # Light theme
        self.available_themes["Light"] = {
            "name": "Light",
            "description": "Light theme for NebulaFusion browser.",
            "author": "NebulaFusion Team",
            "version": "1.0.0",
            "dark": False,
            "stylesheet": self._get_light_stylesheet(),
            "colors": {
                "primary": "#6200EE",
                "secondary": "#03DAC6",
                "accent": "#BB86FC",
                "background": "#FFFFFF",
                "foreground": "#000000",
                "surface": "#F5F5F5",
                "error": "#B00020",
                "warning": "#FB8C00",
                "success": "#4CAF50",
                "info": "#2196F3",
            },
        }

        # Neon theme
        self.available_themes["Neon"] = {
            "name": "Neon",
            "description": "Neon theme for NebulaFusion browser.",
            "author": "NebulaFusion Team",
            "version": "1.0.0",
            "dark": True,
            "stylesheet": self._get_neon_stylesheet(),
            "colors": {
                "primary": "#FF00FF",
                "secondary": "#00FFFF",
                "accent": "#FFFF00",
                "background": "#000000",
                "foreground": "#FFFFFF",
                "surface": "#1A1A1A",
                "error": "#FF0000",
                "warning": "#FFFF00",
                "success": "#00FF00",
                "info": "#00FFFF",
            },
        }

        # Minimal theme
        self.available_themes["Minimal"] = {
            "name": "Minimal",
            "description": "Minimal theme for NebulaFusion browser.",
            "author": "NebulaFusion Team",
            "version": "1.0.0",
            "dark": False,
            "stylesheet": self._get_minimal_stylesheet(),
            "colors": {
                "primary": "#000000",
                "secondary": "#666666",
                "accent": "#CCCCCC",
                "background": "#FFFFFF",
                "foreground": "#000000",
                "surface": "#F5F5F5",
                "error": "#FF0000",
                "warning": "#FFA500",
                "success": "#008000",
                "info": "#0000FF",
            },
        }

    def _load_theme(self, theme_path):
        """Load a theme from a path."""
        try:
            # Load theme.json
            theme_json_path = os.path.join(theme_path, "theme.json")
            with open(theme_json_path, "r") as f:
                theme_data = json.load(f)

            # Validate theme data
            required_fields = ["name", "description", "author", "version", "dark"]
            for field in required_fields:
                if field not in theme_data:
                    self.app_controller.logger.warning(
                        f"Missing required field in theme: {field}"
                    )
                    return

            # Load stylesheet
            stylesheet_path = os.path.join(theme_path, "stylesheet.qss")
            if os.path.exists(stylesheet_path):
                with open(stylesheet_path, "r") as f:
                    theme_data["stylesheet"] = f.read()
            else:
                theme_data["stylesheet"] = ""

            # Add theme
            self.available_themes[theme_data["name"]] = theme_data

            # Emit signal
            self.theme_loaded.emit(theme_data["name"])

            self.app_controller.logger.info(f"Theme loaded: {theme_data['name']}")

        except Exception as e:
            self.app_controller.logger.error(f"Error loading theme: {e}")

    def apply_theme(self, theme_name):
        """Apply a theme."""
        # Check if theme exists
        if theme_name not in self.available_themes:
            self.app_controller.logger.warning(f"Theme not found: {theme_name}")

            # Apply default theme
            if "Default" in self.available_themes:
                theme_name = "Default"
            else:
                return False

        # Get theme
        theme = self.available_themes[theme_name]

        # Apply stylesheet
        if "stylesheet" in theme:
            QApplication.instance().setStyleSheet(theme["stylesheet"])

        # Update current theme
        self.current_theme = theme_name

        # Save theme setting
        self.app_controller.settings_manager.set_setting(
            "appearance.theme", theme_name
        )

        # Emit signal
        self.theme_changed.emit(theme_name)

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onThemeChanged", theme_name, theme
        )

        self.app_controller.logger.info(f"Theme applied: {theme_name}")

        return True

    def get_current_theme(self):
        """Get the current theme."""
        if self.current_theme:
            return self.available_themes[self.current_theme]
        return None

    def get_theme(self, theme_name):
        """Get a theme by name."""
        return self.available_themes.get(theme_name)

    def get_themes(self):
        """Get all available themes."""
        return self.available_themes

    def is_dark_mode(self):
        """Check if dark mode is enabled."""
        current_theme = self.get_current_theme()
        if current_theme:
            return current_theme.get("dark", False)
        return False

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        if self.is_dark_mode():
            # Switch to light theme
            if "Light" in self.available_themes:
                return self.apply_theme("Light")
            elif "Default" in self.available_themes:
                return self.apply_theme("Default")
        else:
            # Switch to dark theme
            if "Dark" in self.available_themes:
                return self.apply_theme("Dark")

        return False

    def create_theme(self, theme_data, save=True):
        """Create a new theme."""
        try:
            # Validate theme data
            required_fields = [
                "name",
                "description",
                "author",
                "version",
                "dark",
                "stylesheet",
                "colors",
            ]
            for field in required_fields:
                if field not in theme_data:
                    self.app_controller.logger.warning(
                        f"Missing required field in theme: {field}"
                    )
                    return False

            # Add theme
            self.available_themes[theme_data["name"]] = theme_data

            # Save theme
            if save:
                self._save_theme(theme_data)

            # Emit signal
            self.theme_loaded.emit(theme_data["name"])

            self.app_controller.logger.info(f"Theme created: {theme_data['name']}")

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error creating theme: {e}")
            return False

    def _save_theme(self, theme_data):
        """Save a theme to disk."""
        try:
            # Create theme directory
            theme_dir = os.path.join(self.default_theme_dir, theme_data["name"])
            os.makedirs(theme_dir, exist_ok=True)

            # Save theme.json
            theme_json = theme_data.copy()
            if "stylesheet" in theme_json:
                del theme_json["stylesheet"]

            with open(os.path.join(theme_dir, "theme.json"), "w") as f:
                json.dump(theme_json, f, indent=4)

            # Save stylesheet
            if "stylesheet" in theme_data:
                with open(os.path.join(theme_dir, "stylesheet.qss"), "w") as f:
                    f.write(theme_data["stylesheet"])

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error saving theme: {e}")
            return False

    def delete_theme(self, theme_name):
        """Delete a theme."""
        try:
            # Check if theme exists
            if theme_name not in self.available_themes:
                self.app_controller.logger.warning(f"Theme not found: {theme_name}")
                return False

            # Check if theme is built-in
            if theme_name in ["Default", "Dark", "Light", "Neon", "Minimal"]:
                self.app_controller.logger.warning(
                    f"Cannot delete built-in theme: {theme_name}"
                )
                return False

            # Check if theme is current
            if theme_name == self.current_theme:
                # Apply default theme
                self.apply_theme("Default")

            # Remove theme
            del self.available_themes[theme_name]

            # Delete theme directory
            theme_dir = os.path.join(self.default_theme_dir, theme_name)
            if os.path.exists(theme_dir):
                import shutil

                shutil.rmtree(theme_dir)

            self.app_controller.logger.info(f"Theme deleted: {theme_name}")

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error deleting theme: {e}")
            return False

    def _get_default_stylesheet(self):
        """Get the default stylesheet."""
        return """
/* Default Theme for NebulaFusion Browser */

/* Main Window */
QMainWindow {
    background-color: #FFFFFF;
    color: #202124;
}

/* Menu Bar */
QMenuBar {
    background-color: #F8F9FA;
    color: #202124;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QMenuBar::item:pressed {
    background-color: #D2E3FC;
    color: #1A73E8;
}

/* Menu */
QMenu {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
}

QMenu::item {
    padding: 6px 25px 6px 20px;
}

QMenu::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QMenu::separator {
    height: 1px;
    background-color: #DADCE0;
    margin: 4px 0px;
}

/* Toolbar */
QToolBar {
    background-color: #F8F9FA;
    border-bottom: 1px solid #DADCE0;
    spacing: 2px;
    padding: 2px;
}

QToolBar::separator {
    width: 1px;
    background-color: #DADCE0;
    margin: 0px 4px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
    color: #202124; /* Ensure readability against light backgrounds */
}

QToolButton:hover {
    background-color: #E8F0FE;
    border: 1px solid #D2E3FC;
}

QToolButton:pressed {
    background-color: #D2E3FC;
}

QToolButton:checked {
    background-color: #D2E3FC;
    border: 1px solid #4285F4;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #DADCE0;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F8F9FA;
    color: #5F6368;
    border: 1px solid #DADCE0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #202124;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #E8F0FE;
}

QTabBar::close-button {
    image: url(:/icons/close.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    background-color: #E8F0FE;
    border-radius: 2px;
}

/* Line Edit (Address Bar) */
QLineEdit {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #D2E3FC;
}

QLineEdit:focus {
    border: 1px solid #4285F4;
}

/* Push Button */
QPushButton {
    background-color: #4285F4;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #5094FC;
}

QPushButton:pressed {
    background-color: #3367D6;
}

QPushButton:disabled {
    background-color: #DADCE0;
    color: #9AA0A6;
}

/* Combo Box */
QComboBox {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #4285F4;
}

QComboBox:on {
    border: 1px solid #4285F4;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #DADCE0;
}

QComboBox::down-arrow {
    image: url(:/icons/dropdown.png);
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    selection-background-color: #E8F0FE;
    selection-color: #1A73E8;
}

/* Check Box */
QCheckBox {
    color: #202124;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    image: url(:/icons/checkbox_unchecked.png);
}

QCheckBox::indicator:checked {
    image: url(:/icons/checkbox_checked.png);
}

/* Radio Button */
QRadioButton {
    color: #202124;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    image: url(:/icons/radio_unchecked.png);
}

QRadioButton::indicator:checked {
    image: url(:/icons/radio_checked.png);
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #DADCE0;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #4285F4;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #5094FC;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #DADCE0;
    border-radius: 4px;
    background-color: #F8F9FA;
    text-align: center;
    color: #202124;
}

QProgressBar::chunk {
    background-color: #4285F4;
    width: 1px;
}

/* Scroll Bar */
QScrollBar:vertical {
    border: none;
    background-color: #F8F9FA;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #DADCE0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #BABCBE;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #F8F9FA;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #DADCE0;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #BABCBE;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #F8F9FA;
    color: #5F6368;
    border-top: 1px solid #DADCE0;
}

QStatusBar::item {
    border: none;
}

/* Dialog */
QDialog {
    background-color: #FFFFFF;
    color: #202124;
}

QDialog QLabel {
    color: #202124;
}

/* Group Box */
QGroupBox {
    border: 1px solid #DADCE0;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 10px;
    color: #202124;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #5F6368;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 6px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #4285F4;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #DADCE0;
    border-bottom: 1px solid #DADCE0;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #DADCE0;
    border-top: 1px solid #DADCE0;
}

/* Text Edit */
QTextEdit {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    selection-background-color: #D2E3FC;
}

QTextEdit:focus {
    border: 1px solid #4285F4;
}

/* List Widget */
QListWidget {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
}

QListWidget::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QListWidget::item:hover {
    background-color: #F8F9FA;
}

/* Tree Widget */
QTreeWidget {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
}

QTreeWidget::item {
    padding: 4px;
}

QTreeWidget::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QTreeWidget::item:hover {
    background-color: #F8F9FA;
}

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    gridline-color: #DADCE0;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

QHeaderView::section {
    background-color: #F8F9FA;
    color: #5F6368;
    padding: 4px;
    border: 1px solid #DADCE0;
    border-left: none;
    border-top: none;
}

QHeaderView::section:first {
    border-left: 1px solid #DADCE0;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #FFFFFF;
    color: #202124;
}

QCalendarWidget QToolButton {
    color: #202124;
    background-color: #F8F9FA;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QMenu {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
}

QCalendarWidget QSpinBox {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #FFFFFF;
    color: #202124;
    selection-background-color: #E8F0FE;
    selection-color: #1A73E8;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #9AA0A6;
}

/* Tool Box */
QToolBox::tab {
    background-color: #F8F9FA;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 4px;
}

QToolBox::tab:selected {
    background-color: #E8F0FE;
    color: #1A73E8;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(:/icons/close.png);
    titlebar-normal-icon: url(:/icons/undock.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #F8F9FA;
    color: #202124;
    padding: 4px;
    border: 1px solid #DADCE0;
}

/* MDI Area */
QMdiArea {
    background-color: #F8F9FA;
}

QMdiSubWindow {
    background-color: #FFFFFF;
    border: 1px solid #DADCE0;
}

QMdiSubWindow::title {
    background-color: #F8F9FA;
    color: #202124;
}

/* Splitter */
QSplitter::handle {
    background-color: #DADCE0;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #4285F4;
}

/* ToolTip */
QToolTip {
    background-color: #FFFFFF;
    color: #202124;
    border: 1px solid #DADCE0;
    border-radius: 4px;
    padding: 4px;
}

/* WebView */
QWebEngineView {
    background-color: #FFFFFF;
}
"""

    def _get_dark_stylesheet(self):
        """Get the dark stylesheet."""
        return """
/* Dark Theme for NebulaFusion Browser */

/* Main Window */
QMainWindow {
    background-color: #121212;
    color: #E1E1E1;
}

/* Menu Bar */
QMenuBar {
    background-color: #1E1E1E;
    color: #E1E1E1;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

QMenuBar::item:pressed {
    background-color: #6200EE;
    color: #E1E1E1;
}

/* Menu */
QMenu {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
}

QMenu::item {
    padding: 6px 25px 6px 20px;
}

QMenu::item:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

QMenu::separator {
    height: 1px;
    background-color: #333333;
    margin: 4px 0px;
}

/* Toolbar */
QToolBar {
    background-color: #1E1E1E;
    border-bottom: 1px solid #333333;
    spacing: 2px;
    padding: 2px;
}

QToolBar::separator {
    width: 1px;
    background-color: #333333;
    margin: 0px 4px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
    color: #E1E1E1; /* Ensure readability against dark backgrounds */
}

QToolButton:hover {
    background-color: #3700B3;
    border: 1px solid #6200EE;
}

QToolButton:pressed {
    background-color: #6200EE;
}

QToolButton:checked {
    background-color: #6200EE;
    border: 1px solid #BB86FC;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #121212;
}

QTabBar::tab {
    background-color: #1E1E1E;
    color: #9E9E9E;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #121212;
    color: #E1E1E1;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #3700B3;
}

QTabBar::close-button {
    image: url(:/icons/close_dark.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    background-color: #3700B3;
    border-radius: 2px;
}

/* Line Edit (Address Bar) */
QLineEdit {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #6200EE;
}

QLineEdit:focus {
    border: 1px solid #BB86FC;
}

/* Push Button */
QPushButton {
    background-color: #BB86FC;
    color: #121212;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #DDB8FF;
}

QPushButton:pressed {
    background-color: #9965D4;
}

QPushButton:disabled {
    background-color: #333333;
    color: #757575;
}

/* Combo Box */
QComboBox {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #BB86FC;
}

QComboBox:on {
    border: 1px solid #BB86FC;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #333333;
}

QComboBox::down-arrow {
    image: url(:/icons/dropdown_dark.png);
}

QComboBox QAbstractItemView {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    selection-background-color: #3700B3;
    selection-color: #E1E1E1;
}

/* Check Box */
QCheckBox {
    color: #E1E1E1;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    image: url(:/icons/checkbox_unchecked_dark.png);
}

QCheckBox::indicator:checked {
    image: url(:/icons/checkbox_checked_dark.png);
}

/* Radio Button */
QRadioButton {
    color: #E1E1E1;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    image: url(:/icons/radio_unchecked_dark.png);
}

QRadioButton::indicator:checked {
    image: url(:/icons/radio_checked_dark.png);
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #333333;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #BB86FC;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #DDB8FF;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #333333;
    border-radius: 4px;
    background-color: #1E1E1E;
    text-align: center;
    color: #E1E1E1;
}

QProgressBar::chunk {
    background-color: #BB86FC;
    width: 1px;
}

/* Scroll Bar */
QScrollBar:vertical {
    border: none;
    background-color: #1E1E1E;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #333333;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #444444;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #1E1E1E;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #333333;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #444444;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #1E1E1E;
    color: #9E9E9E;
    border-top: 1px solid #333333;
}

QStatusBar::item {
    border: none;
}

/* Dialog */
QDialog {
    background-color: #121212;
    color: #E1E1E1;
}

QDialog QLabel {
    color: #E1E1E1;
}

/* Group Box */
QGroupBox {
    border: 1px solid #333333;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 10px;
    color: #E1E1E1;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #9E9E9E;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #BB86FC;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #333333;
    border-bottom: 1px solid #333333;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #333333;
    border-top: 1px solid #333333;
}

/* Text Edit */
QTextEdit {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    selection-background-color: #6200EE;
}

QTextEdit:focus {
    border: 1px solid #BB86FC;
}

/* List Widget */
QListWidget {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
}

QListWidget::item:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

QListWidget::item:hover {
    background-color: #2A2A2A;
}

/* Tree Widget */
QTreeWidget {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
}

QTreeWidget::item {
    padding: 4px;
}

QTreeWidget::item:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

QTreeWidget::item:hover {
    background-color: #2A2A2A;
}

/* Table Widget */
QTableWidget {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    gridline-color: #333333;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

QHeaderView::section {
    background-color: #1E1E1E;
    color: #9E9E9E;
    padding: 4px;
    border: 1px solid #333333;
    border-left: none;
    border-top: none;
}

QHeaderView::section:first {
    border-left: 1px solid #333333;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #121212;
    color: #E1E1E1;
}

QCalendarWidget QToolButton {
    color: #E1E1E1;
    background-color: #1E1E1E;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QMenu {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
}

QCalendarWidget QSpinBox {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #1E1E1E;
    color: #E1E1E1;
    selection-background-color: #3700B3;
    selection-color: #E1E1E1;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #757575;
}

/* Tool Box */
QToolBox::tab {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QToolBox::tab:selected {
    background-color: #3700B3;
    color: #E1E1E1;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(:/icons/close_dark.png);
    titlebar-normal-icon: url(:/icons/undock_dark.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #1E1E1E;
    color: #E1E1E1;
    padding: 4px;
    border: 1px solid #333333;
}

/* MDI Area */
QMdiArea {
    background-color: #1E1E1E;
}

QMdiSubWindow {
    background-color: #121212;
    border: 1px solid #333333;
}

QMdiSubWindow::title {
    background-color: #1E1E1E;
    color: #E1E1E1;
}

/* Splitter */
QSplitter::handle {
    background-color: #333333;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #BB86FC;
}

/* ToolTip */
QToolTip {
    background-color: #1E1E1E;
    color: #E1E1E1;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

/* WebView */
QWebEngineView {
    background-color: #121212;
}
"""

    def _get_light_stylesheet(self):
        """Get the light stylesheet."""
        return """
/* Light Theme for NebulaFusion Browser */

/* Main Window */
QMainWindow {
    background-color: #FFFFFF;
    color: #000000;
}

/* Menu Bar */
QMenuBar {
    background-color: #F5F5F5;
    color: #000000;
    border: none;
}

QMenuBar::item {
    background-color: transparent;
    color: #000000 !important;
    padding: 4px 10px;
    margin: 2px 2px;
    border-radius: 3px;
}

QMenuBar::item:enabled {
    color: #000000 !important;
}

QMenuBar::item:disabled {
    color: #808080 !important;
}

QMenuBar::item:selected {
    background-color: #E0E0E0;
    color: #000000;
}

QMenuBar::item:pressed {
    background-color: #D0D0D0;
    color: #000000;
}

/* Menu */
QMenu {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
}

QMenu::item {
    padding: 6px 25px 6px 20px;
}

QMenu::item:selected {
    background-color: #E0E0E0;
    color: #6200EE;
}

QMenu::separator {
    height: 1px;
    background-color: #E0E0E0;
    margin: 4px 0px;
}

/* Toolbar */
QToolBar {
    background-color: #F5F5F5;
    border-bottom: 1px solid #E0E0E0;
    spacing: 2px;
    padding: 2px;
}

QToolBar::separator {
    width: 1px;
    background-color: #E0E0E0;
    margin: 0px 4px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
    color: #000000; /* Ensure readability against light backgrounds */
}

QToolButton:hover {
    background-color: #E0E0E0;
    border: 1px solid #D0D0D0;
}

QToolButton:pressed {
    background-color: #D0D0D0;
}

QToolButton:checked {
    background-color: #D0D0D0;
    border: 1px solid #6200EE;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #E0E0E0;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F5F5F5;
    color: #757575;
    border: 1px solid #E0E0E0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #E0E0E0;
}

QTabBar::close-button {
    image: url(:/icons/close.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    background-color: #E0E0E0;
    border-radius: 2px;
}

/* Line Edit (Address Bar) */
QLineEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #D0D0D0;
}

QLineEdit:focus {
    border: 1px solid #6200EE;
}

/* Push Button */
QPushButton {
    background-color: #6200EE;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #7722FF;
}

QPushButton:pressed {
    background-color: #5000CC;
}

QPushButton:disabled {
    background-color: #E0E0E0;
    color: #9E9E9E;
}

/* Combo Box */
QComboBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #6200EE;
}

QComboBox:on {
    border: 1px solid #6200EE;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #E0E0E0;
}

QComboBox::down-arrow {
    image: url(:/icons/dropdown.png);
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    selection-background-color: #E0E0E0;
    selection-color: #6200EE;
}

/* Check Box */
QCheckBox {
    color: #000000;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    image: url(:/icons/checkbox_unchecked.png);
}

QCheckBox::indicator:checked {
    image: url(:/icons/checkbox_checked.png);
}

/* Radio Button */
QRadioButton {
    color: #000000;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    image: url(:/icons/radio_unchecked.png);
}

QRadioButton::indicator:checked {
    image: url(:/icons/radio_checked.png);
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #E0E0E0;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #6200EE;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #7722FF;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    background-color: #F5F5F5;
    text-align: center;
    color: #000000;
}

QProgressBar::chunk {
    background-color: #6200EE;
    width: 1px;
}

/* Scroll Bar */
QScrollBar:vertical {
    border: none;
    background-color: #F5F5F5;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #E0E0E0;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #D0D0D0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #F5F5F5;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #E0E0E0;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #D0D0D0;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #F5F5F5;
    color: #757575;
    border-top: 1px solid #E0E0E0;
}

QStatusBar::item {
    border: none;
}

/* Dialog */
QDialog {
    background-color: #FFFFFF;
    color: #000000;
}

QDialog QLabel {
    color: #000000;
}

/* Group Box */
QGroupBox {
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 10px;
    color: #000000;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #757575;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 6px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #6200EE;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #E0E0E0;
    border-bottom: 1px solid #E0E0E0;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #E0E0E0;
    border-top: 1px solid #E0E0E0;
}

/* Text Edit */
QTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    selection-background-color: #D0D0D0;
}

QTextEdit:focus {
    border: 1px solid #6200EE;
}

/* List Widget */
QListWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
}

QListWidget::item:selected {
    background-color: #E0E0E0;
    color: #6200EE;
}

QListWidget::item:hover {
    background-color: #F5F5F5;
}

/* Tree Widget */
QTreeWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
}

QTreeWidget::item {
    padding: 4px;
}

QTreeWidget::item:selected {
    background-color: #E0E0E0;
    color: #6200EE;
}

QTreeWidget::item:hover {
    background-color: #F5F5F5;
}

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    gridline-color: #E0E0E0;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #E0E0E0;
    color: #6200EE;
}

QHeaderView::section {
    background-color: #F5F5F5;
    color: #757575;
    padding: 4px;
    border: 1px solid #E0E0E0;
    border-left: none;
    border-top: none;
}

QHeaderView::section:first {
    border-left: 1px solid #E0E0E0;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #FFFFFF;
    color: #000000;
}

QCalendarWidget QToolButton {
    color: #000000;
    background-color: #F5F5F5;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QMenu {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
}

QCalendarWidget QSpinBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #FFFFFF;
    color: #000000;
    selection-background-color: #E0E0E0;
    selection-color: #6200EE;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #9E9E9E;
}

/* Tool Box */
QToolBox::tab {
    background-color: #F5F5F5;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 4px;
}

QToolBox::tab:selected {
    background-color: #E0E0E0;
    color: #6200EE;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(:/icons/close.png);
    titlebar-normal-icon: url(:/icons/undock.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #F5F5F5;
    color: #000000;
    padding: 4px;
    border: 1px solid #E0E0E0;
}

/* MDI Area */
QMdiArea {
    background-color: #F5F5F5;
}

QMdiSubWindow {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
}

QMdiSubWindow::title {
    background-color: #F5F5F5;
    color: #000000;
}

/* Splitter */
QSplitter::handle {
    background-color: #E0E0E0;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #6200EE;
}

/* ToolTip */
QToolTip {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    padding: 4px;
}

/* WebView */
QWebEngineView {
    background-color: #FFFFFF;
}
"""

    def _get_neon_stylesheet(self):
        """Get the neon stylesheet."""
        return """
/* Neon Theme for NebulaFusion Browser */

/* Main Window */
QMainWindow {
    background-color: #000000;
    color: #FFFFFF;
}

/* Menu Bar */
QMenuBar {
    background-color: #1A1A1A;
    color: #FFFFFF;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background-color: #FF00FF;
    color: #000000;
}

QMenuBar::item:pressed {
    background-color: #CC00CC;
    color: #000000;
}

/* Menu */
QMenu {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
}

QMenu::item {
    padding: 6px 25px 6px 20px;
}

QMenu::item:selected {
    background-color: #FF00FF;
    color: #000000;
}

QMenu::separator {
    height: 1px;
    background-color: #333333;
    margin: 4px 0px;
}

/* Toolbar */
QToolBar {
    background-color: #1A1A1A;
    border-bottom: 1px solid #333333;
    spacing: 2px;
    padding: 2px;
}

QToolBar::separator {
    width: 1px;
    background-color: #333333;
    margin: 0px 4px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
    color: #FFFFFF; /* Ensure readability against dark backgrounds */
}

QToolButton:hover {
    background-color: #FF00FF;
    border: 1px solid #CC00CC;
    color: #000000;
}

QToolButton:pressed {
    background-color: #CC00CC;
    color: #000000;
}

QToolButton:checked {
    background-color: #CC00CC;
    border: 1px solid #FF00FF;
    color: #000000;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #000000;
}

QTabBar::tab {
    background-color: #1A1A1A;
    color: #CCCCCC;
    border: 1px solid #333333;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #000000;
    color: #FF00FF;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #333333;
    color: #00FFFF;
}

QTabBar::close-button {
    image: url(:/icons/close_neon.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    background-color: #FF00FF;
    border-radius: 2px;
}

/* Line Edit (Address Bar) */
QLineEdit {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
    selection-background-color: #FF00FF;
}

QLineEdit:focus {
    border: 1px solid #FF00FF;
}

/* Push Button */
QPushButton {
    background-color: #FF00FF;
    color: #000000;
    border: none;
    border-radius: 4px;
    padding: 6px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #FF33FF;
}

QPushButton:pressed {
    background-color: #CC00CC;
}

QPushButton:disabled {
    background-color: #333333;
    color: #666666;
}

/* Combo Box */
QComboBox {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #FF00FF;
}

QComboBox:on {
    border: 1px solid #FF00FF;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #333333;
}

QComboBox::down-arrow {
    image: url(:/icons/dropdown_neon.png);
}

QComboBox QAbstractItemView {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    selection-background-color: #FF00FF;
    selection-color: #000000;
}

/* Check Box */
QCheckBox {
    color: #FFFFFF;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    image: url(:/icons/checkbox_unchecked_neon.png);
}

QCheckBox::indicator:checked {
    image: url(:/icons/checkbox_checked_neon.png);
}

/* Radio Button */
QRadioButton {
    color: #FFFFFF;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    image: url(:/icons/radio_unchecked_neon.png);
}

QRadioButton::indicator:checked {
    image: url(:/icons/radio_checked_neon.png);
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #333333;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #FF00FF;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #FF33FF;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #333333;
    border-radius: 4px;
    background-color: #1A1A1A;
    text-align: center;
    color: #FFFFFF;
}

QProgressBar::chunk {
    background-color: #FF00FF;
    width: 1px;
}

/* Scroll Bar */
QScrollBar:vertical {
    border: none;
    background-color: #1A1A1A;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #333333;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #FF00FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #1A1A1A;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #333333;
    min-width: 20px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #FF00FF;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1A1A;
    color: #CCCCCC;
    border-top: 1px solid #333333;
}

QStatusBar::item {
    border: none;
}

/* Dialog */
QDialog {
    background-color: #000000;
    color: #FFFFFF;
}

QDialog QLabel {
    color: #FFFFFF;
}

/* Group Box */
QGroupBox {
    border: 1px solid #333333;
    border-radius: 4px;
    margin-top: 1ex;
    padding-top: 10px;
    color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #CCCCCC;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #FF00FF;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #333333;
    border-bottom: 1px solid #333333;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #333333;
    border-top: 1px solid #333333;
}

/* Text Edit */
QTextEdit {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    selection-background-color: #FF00FF;
}

QTextEdit:focus {
    border: 1px solid #FF00FF;
}

/* List Widget */
QListWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
}

QListWidget::item {
    padding: 4px;
}

QListWidget::item:selected {
    background-color: #FF00FF;
    color: #000000;
}

QListWidget::item:hover {
    background-color: #333333;
}

/* Tree Widget */
QTreeWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
}

QTreeWidget::item {
    padding: 4px;
}

QTreeWidget::item:selected {
    background-color: #FF00FF;
    color: #000000;
}

QTreeWidget::item:hover {
    background-color: #333333;
}

/* Table Widget */
QTableWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    gridline-color: #333333;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #FF00FF;
    color: #000000;
}

QHeaderView::section {
    background-color: #1A1A1A;
    color: #CCCCCC;
    padding: 4px;
    border: 1px solid #333333;
    border-left: none;
    border-top: none;
}

QHeaderView::section:first {
    border-left: 1px solid #333333;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #000000;
    color: #FFFFFF;
}

QCalendarWidget QToolButton {
    color: #FFFFFF;
    background-color: #1A1A1A;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QMenu {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
}

QCalendarWidget QSpinBox {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #1A1A1A;
    color: #FFFFFF;
    selection-background-color: #FF00FF;
    selection-color: #000000;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #666666;
}

/* Tool Box */
QToolBox::tab {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

QToolBox::tab:selected {
    background-color: #FF00FF;
    color: #000000;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(:/icons/close_neon.png);
    titlebar-normal-icon: url(:/icons/undock_neon.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #1A1A1A;
    color: #FFFFFF;
    padding: 4px;
    border: 1px solid #333333;
}

/* MDI Area */
QMdiArea {
    background-color: #1A1A1A;
}

QMdiSubWindow {
    background-color: #000000;
    border: 1px solid #333333;
}

QMdiSubWindow::title {
    background-color: #1A1A1A;
    color: #FFFFFF;
}

/* Splitter */
QSplitter::handle {
    background-color: #333333;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #FF00FF;
}

/* ToolTip */
QToolTip {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}

/* WebView */
QWebEngineView {
    background-color: #000000;
}
"""

    def _get_minimal_stylesheet(self):
        """Get the minimal stylesheet."""
        return """
/* Minimal Theme for NebulaFusion Browser */

/* Main Window */
QMainWindow {
    background-color: #FFFFFF;
    color: #000000;
}

/* Menu Bar */
QMenuBar {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom: 1px solid #CCCCCC;
}

QMenuBar::item {
    background-color: transparent;
    padding: 4px 10px;
}

QMenuBar::item:selected {
    background-color: #EEEEEE;
}

QMenuBar::item:pressed {
    background-color: #DDDDDD;
}

/* Menu */
QMenu {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
}

QMenu::item {
    padding: 6px 25px 6px 20px;
}

QMenu::item:selected {
    background-color: #EEEEEE;
}

QMenu::separator {
    height: 1px;
    background-color: #CCCCCC;
    margin: 4px 0px;
}

/* Toolbar */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #CCCCCC;
    spacing: 2px;
    padding: 2px;
}

QToolBar::separator {
    width: 1px;
    background-color: #CCCCCC;
    margin: 0px 4px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #EEEEEE;
}

QToolButton:pressed {
    background-color: #DDDDDD;
}

QToolButton:checked {
    background-color: #DDDDDD;
    border: 1px solid #CCCCCC;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #CCCCCC;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #FFFFFF;
    color: #666666;
    border: 1px solid #CCCCCC;
    border-bottom: none;
    padding: 6px 10px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #000000;
    border-bottom: none;
}

QTabBar::tab:hover:!selected {
    background-color: #EEEEEE;
}

QTabBar::close-button {
    image: url(:/icons/close_minimal.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    background-color: #EEEEEE;
    border-radius: 2px;
}

/* Line Edit (Address Bar) */
QLineEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 6px;
    selection-background-color: #DDDDDD;
}

QLineEdit:focus {
    border: 1px solid #999999;
}

/* Push Button */
QPushButton {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 6px 16px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #EEEEEE;
}

QPushButton:pressed {
    background-color: #DDDDDD;
}

QPushButton:disabled {
    background-color: #F5F5F5;
    color: #AAAAAA;
    border: 1px solid #DDDDDD;
}

/* Combo Box */
QComboBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 6px;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #999999;
}

QComboBox:on {
    border: 1px solid #999999;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #CCCCCC;
}

QComboBox::down-arrow {
    image: url(:/icons/dropdown_minimal.png);
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    selection-background-color: #EEEEEE;
}

/* Check Box */
QCheckBox {
    color: #000000;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    image: url(:/icons/checkbox_unchecked_minimal.png);
}

QCheckBox::indicator:checked {
    image: url(:/icons/checkbox_checked_minimal.png);
}

/* Radio Button */
QRadioButton {
    color: #000000;
    spacing: 5px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    image: url(:/icons/radio_unchecked_minimal.png);
}

QRadioButton::indicator:checked {
    image: url(:/icons/radio_checked_minimal.png);
}

/* Slider */
QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background-color: #CCCCCC;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #000000;
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background-color: #333333;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    background-color: #FFFFFF;
    text-align: center;
    color: #000000;
}

QProgressBar::chunk {
    background-color: #000000;
    width: 1px;
}

/* Scroll Bar */
QScrollBar:vertical {
    border: none;
    background-color: #FFFFFF;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #CCCCCC;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #AAAAAA;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #FFFFFF;
    height: 8px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #CCCCCC;
    min-width: 20px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #AAAAAA;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #FFFFFF;
    color: #666666;
    border-top: 1px solid #CCCCCC;
}

QStatusBar::item {
    border: none;
}

/* Dialog */
QDialog {
    background-color: #FFFFFF;
    color: #000000;
}

QDialog QLabel {
    color: #000000;
}

/* Group Box */
QGroupBox {
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    margin-top: 1ex;
    padding-top: 10px;
    color: #000000;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #666666;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 6px;
}

QSpinBox:hover, QDoubleSpinBox:hover {
    border: 1px solid #999999;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 16px;
    border-left: 1px solid #CCCCCC;
    border-bottom: 1px solid #CCCCCC;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 16px;
    border-left: 1px solid #CCCCCC;
    border-top: 1px solid #CCCCCC;
}

/* Text Edit */
QTextEdit {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    selection-background-color: #DDDDDD;
}

QTextEdit:focus {
    border: 1px solid #999999;
}

/* List Widget */
QListWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
}

QListWidget::item {
    padding: 4px;
}

QListWidget::item:selected {
    background-color: #EEEEEE;
    color: #000000;
}

QListWidget::item:hover {
    background-color: #F5F5F5;
}

/* Tree Widget */
QTreeWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
}

QTreeWidget::item {
    padding: 4px;
}

QTreeWidget::item:selected {
    background-color: #EEEEEE;
    color: #000000;
}

QTreeWidget::item:hover {
    background-color: #F5F5F5;
}

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    gridline-color: #CCCCCC;
}

QTableWidget::item {
    padding: 4px;
}

QTableWidget::item:selected {
    background-color: #EEEEEE;
    color: #000000;
}

QHeaderView::section {
    background-color: #FFFFFF;
    color: #666666;
    padding: 4px;
    border: 1px solid #CCCCCC;
    border-left: none;
    border-top: none;
}

QHeaderView::section:first {
    border-left: 1px solid #CCCCCC;
}

/* Calendar Widget */
QCalendarWidget {
    background-color: #FFFFFF;
    color: #000000;
}

QCalendarWidget QToolButton {
    color: #000000;
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 4px;
}

QCalendarWidget QMenu {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
}

QCalendarWidget QSpinBox {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 4px;
}

QCalendarWidget QAbstractItemView:enabled {
    background-color: #FFFFFF;
    color: #000000;
    selection-background-color: #EEEEEE;
    selection-color: #000000;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #AAAAAA;
}

/* Tool Box */
QToolBox::tab {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 4px;
}

QToolBox::tab:selected {
    background-color: #EEEEEE;
    color: #000000;
}

/* Dock Widget */
QDockWidget {
    titlebar-close-icon: url(:/icons/close_minimal.png);
    titlebar-normal-icon: url(:/icons/undock_minimal.png);
}

QDockWidget::title {
    text-align: left;
    background-color: #FFFFFF;
    color: #000000;
    padding: 4px;
    border: 1px solid #CCCCCC;
}

/* MDI Area */
QMdiArea {
    background-color: #F5F5F5;
}

QMdiSubWindow {
    background-color: #FFFFFF;
    border: 1px solid #CCCCCC;
}

QMdiSubWindow::title {
    background-color: #FFFFFF;
    color: #000000;
}

/* Splitter */
QSplitter::handle {
    background-color: #CCCCCC;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}

QSplitter::handle:hover {
    background-color: #999999;
}

/* ToolTip */
QToolTip {
    background-color: #FFFFFF;
    color: #000000;
    border: 1px solid #CCCCCC;
    border-radius: 2px;
    padding: 4px;
}

/* WebView */
QWebEngineView {
    background-color: #FFFFFF;
}
"""
