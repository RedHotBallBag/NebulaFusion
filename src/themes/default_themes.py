#!/usr/bin/env python3
# NebulaFusion Browser - Default Themes

import os
import sys
import json
import shutil
from PyQt5.QtCore import QObject, pyqtSignal


class DefaultThemes(QObject):
    """
    Provides default themes for the browser.
    """

    # Signals
    theme_created = pyqtSignal(str)

    def __init__(self, app_controller):
        """Initialize the default themes."""
        super().__init__()
        self.app_controller = app_controller

        # Default themes
        self.default_themes = {
            "default": {
                "name": "Default",
                "version": "1.0.0",
                "author": "NebulaFusion",
                "description": "Default theme for NebulaFusion browser.",
                "type": "light",
                "color_scheme": {
                    "primary": "#4a86e8",
                    "secondary": "#f1c232",
                    "background": "#ffffff",
                    "text": "#333333",
                    "accent": "#6aa84f",
                },
            },
            "dark": {
                "name": "Dark",
                "version": "1.0.0",
                "author": "NebulaFusion",
                "description": "Dark theme for NebulaFusion browser.",
                "type": "dark",
                "color_scheme": {
                    "primary": "#4a86e8",
                    "secondary": "#f1c232",
                    "background": "#2d2d2d",
                    "text": "#ffffff",
                    "accent": "#6aa84f",
                },
            },
            "light": {
                "name": "Light",
                "version": "1.0.0",
                "author": "NebulaFusion",
                "description": "Light theme for NebulaFusion browser.",
                "type": "light",
                "color_scheme": {
                    "primary": "#4a86e8",
                    "secondary": "#f1c232",
                    "background": "#ffffff",
                    "text": "#333333",
                    "accent": "#6aa84f",
                },
            },
            "neon": {
                "name": "Neon",
                "version": "1.0.0",
                "author": "NebulaFusion",
                "description": "Neon theme for NebulaFusion browser.",
                "type": "dark",
                "color_scheme": {
                    "primary": "#ff00ff",
                    "secondary": "#00ffff",
                    "background": "#2d2d2d",
                    "text": "#ffffff",
                    "accent": "#ff00ff",
                },
            },
            "minimal": {
                "name": "Minimal",
                "version": "1.0.0",
                "author": "NebulaFusion",
                "description": "Minimal theme for NebulaFusion browser.",
                "type": "light",
                "color_scheme": {
                    "primary": "#4a86e8",
                    "secondary": "#f1c232",
                    "background": "#ffffff",
                    "text": "#333333",
                    "accent": "#6aa84f",
                },
            },
        }

    def create_default_themes(self, themes_dir):
        """Create default themes in the specified directory."""
        # Create themes directory if it doesn't exist
        os.makedirs(themes_dir, exist_ok=True)

        # Create each default theme
        for theme_name, theme_info in self.default_themes.items():
            theme_dir = os.path.join(themes_dir, theme_name)
            if not os.path.exists(theme_dir):
                os.makedirs(theme_dir, exist_ok=True)

                # Create theme.json
                with open(os.path.join(theme_dir, "theme.json"), "w") as f:
                    json.dump(theme_info, f, indent=4)

                # Create style.qss
                style_content = self._generate_style(theme_name, theme_info)
                with open(os.path.join(theme_dir, "style.qss"), "w") as f:
                    f.write(style_content)

                # Create preview.png placeholder
                # In a real implementation, we would create an actual preview image
                with open(os.path.join(theme_dir, "preview.png"), "w") as f:
                    f.write("Preview image placeholder")

                # Emit signal
                self.theme_created.emit(theme_name)

    def _generate_style(self, theme_name, theme_info):
        """Generate style for a theme."""
        # Get color scheme
        colors = theme_info["color_scheme"]

        # Generate style based on theme name
        if theme_name == "default":
            return self._generate_default_style(colors)
        elif theme_name == "dark":
            return self._generate_dark_style(colors)
        elif theme_name == "light":
            return self._generate_light_style(colors)
        elif theme_name == "neon":
            return self._generate_neon_style(colors)
        elif theme_name == "minimal":
            return self._generate_minimal_style(colors)
        else:
            return self._generate_default_style(colors)

    def _generate_default_style(self, colors):
        """Generate default style."""
        return f"""
/* Default Theme */
QMainWindow, QDialog {{
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QTabWidget::pane {{
    border: 1px solid #cccccc;
    background-color: {colors["background"]};
}}

QTabBar::tab {{
    background-color: #e6e6e6;
    color: #333333;
    padding: 6px 12px;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors["background"]};
    border-bottom: 1px solid {colors["background"]};
}}

QTabBar::tab:hover {{
    background-color: #f0f0f0;
}}

QLineEdit {{
    padding: 6px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QPushButton {{
    background-color: {colors["primary"]};
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: #3a76d8;
}}

QPushButton:pressed {{
    background-color: #2a66c8;
}}

QToolBar {{
    background-color: #f5f5f5;
    border-bottom: 1px solid #cccccc;
    spacing: 6px;
    padding: 3px;
}}

QMenuBar {{
    background-color: #f5f5f5; /* Light grey background for menu bar */
    color: #333333; /* Dark text for menu bar */
}}

QMenuBar::item {{
    spacing: 3px;
    padding: 6px 12px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: #e0e0e0; /* Highlight on hover/selection */
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
    color: #333333; /* Ensure readability against light backgrounds */
}}

QToolButton:hover {{
    background-color: #e0e0e0;
}}

QToolButton:pressed {{
    background-color: #d0d0d0;
}}

QMenu {{
    background-color: {colors["background"]};
    color: #333333; /* Ensure readability against light backgrounds */
    border: 1px solid #cccccc;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: {colors["primary"]};
    color: white;
}}

QStatusBar {{
    background-color: #f5f5f5;
    color: #666666;
    border-top: 1px solid #cccccc;
}}

QProgressBar {{
    border: 1px solid #cccccc;
    border-radius: 4px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors["primary"]};
}}
"""

    def _generate_dark_style(self, colors):
        """Generate dark style."""
        return f"""
/* Dark Theme */
QMainWindow, QDialog {{
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QTabWidget::pane {{
    border: 1px solid #444444;
    background-color: {colors["background"]};
}}

QTabBar::tab {{
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 6px 12px;
    border: 1px solid #444444;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors["background"]};
    border-bottom: 1px solid {colors["background"]};
}}

QTabBar::tab:hover {{
    background-color: #4d4d4d;
}}

QLineEdit {{
    padding: 6px;
    border: 1px solid #444444;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: {colors["text"]};
}}

QPushButton {{
    background-color: {colors["primary"]};
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: #3a76d8;
}}

QPushButton:pressed {{
    background-color: #2a66c8;
}}

QToolBar {{
    background-color: #3d3d3d;
    border-bottom: 1px solid #444444;
    spacing: 6px;
    padding: 3px;
}}

QMenuBar {{
    background-color: #3d3d3d; /* Dark grey background for menu bar */
   
}}

QMenuBar::item {{
    spacing: 3px;
    padding: 6px 12px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: #4d4d4d; /* Highlight on hover/selection */
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
    color: #333333; /* Ensure readability against light backgrounds */
}}

QToolButton:hover {{
    background-color: #4d4d4d;
}}

QToolButton:pressed {{
    background-color: #5d5d5d;
}}

QMenu {{
    background-color: {colors["background"]};
    color: #ffffff; /* Ensure readability against dark backgrounds */
    border: 1px solid #444444;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: {colors["primary"]};
    color: white;
}}

QStatusBar {{
    background-color: #3d3d3d;
    color: #b0b0b0;
    border-top: 1px solid #444444;
}}

QProgressBar {{
    border: 1px solid #444444;
    border-radius: 4px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors["primary"]};
}}
"""

    def _generate_light_style(self, colors):
        """Generate light style."""
        return f"""
/* Light Theme */
QMainWindow, QDialog {{
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QTabWidget::pane {{
    border: 1px solid #e0e0e0;
    background-color: {colors["background"]};
}}

QTabBar::tab {{
    background-color: #f0f0f0;
    color: #333333;
    padding: 6px 12px;
    border: 1px solid #e0e0e0;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors["background"]};
    border-bottom: 1px solid {colors["background"]};
}}

QTabBar::tab:hover {{
    background-color: #f8f8f8;
}}

QLineEdit {{
    padding: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QPushButton {{
    background-color: {colors["primary"]};
    color: white;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: #3a76d8;
}}

QPushButton:pressed {{
    background-color: #2a66c8;
}}

QToolBar {{
    background-color: #f8f8f8;
    border-bottom: 1px solid #e0e0e0;
    spacing: 6px;
    padding: 3px;
}}

QMenuBar {{
    background-color: #f8f8f8; /* Light grey background for menu bar */
    color: #333333; /* Dark text for menu bar */
}}

QMenuBar::item {{
    spacing: 3px;
    padding: 6px 12px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: #f0f0f0; /* Highlight on hover/selection */
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
}}

QToolButton:hover {{
    background-color: #f0f0f0;
}}

QToolButton:pressed {{
    background-color: #e8e8e8;
}}

QMenu {{
    background-color: {colors["background"]};
    color: #333333; /* Ensure readability against light backgrounds */
    border: 1px solid #e0e0e0;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: {colors["primary"]};
    color: white;
}}

QStatusBar {{
    background-color: #f8f8f8;
    color: #666666;
    border-top: 1px solid #e0e0e0;
}}

QProgressBar {{
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors["primary"]};
}}
"""

    def _generate_neon_style(self, colors):
        """Generate neon style."""
        return f"""
/* Neon Theme */
QMainWindow, QDialog {{
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QTabWidget::pane {{
    border: 1px solid #444444;
    background-color: {colors["background"]};
}}

QTabBar::tab {{
    background-color: #3d3d3d;
    color: #00ffff;
    padding: 6px 12px;
    border: 1px solid #444444;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:selected {{
    background-color: {colors["background"]};
    border-bottom: 1px solid {colors["background"]};
    color: #ff00ff;
}}

QTabBar::tab:hover {{
    background-color: #4d4d4d;
    color: #ff00ff;
}}

QLineEdit {{
    padding: 6px;
    border: 1px solid #ff00ff;
    border-radius: 4px;
    background-color: #3d3d3d;
    color: #00ffff;
}}

QPushButton {{
    background-color: {colors["primary"]};
    color: #00ffff;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: #ff00aa;
}}

QPushButton:pressed {{
    background-color: #cc0088;
}}

QToolBar {{
    background-color: #3d3d3d;
    border-bottom: 1px solid #ff00ff;
    spacing: 6px;
    padding: 3px;
}}

QMenuBar {{
    background-color: #3d3d3d; /* Dark grey background for menu bar */
    color: #00ffff; /* Neon text for menu bar */
}}

QMenuBar::item {{
    spacing: 3px;
    padding: 6px 12px;
    background: transparent;
}}

QMenuBar::item:selected {{
    background: #4d4d4d; /* Highlight on hover/selection */
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
}}

QToolButton:hover {{
    background-color: #4d4d4d;
}}

QToolButton:pressed {{
    background-color: #5d5d5d;
}}

QMenu {{
    background-color: {colors["background"]};
    color: #ffffff; /* Ensure readability against dark backgrounds */
    border: 1px solid #ff00ff;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: {colors["primary"]};
    color: #00ffff;
}}

QStatusBar {{
    background-color: #3d3d3d;
    color: #00ffff;
    border-top: 1px solid #ff00ff;
}}

QProgressBar {{
    border: 1px solid #ff00ff;
    border-radius: 4px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors["primary"]};
}}
"""

    def _generate_minimal_style(self, colors):
        """Generate minimal style."""
        return f"""
/* Minimal Theme */
QMainWindow, QDialog {{
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QTabWidget::pane {{
    border: none;
    background-color: {colors["background"]};
}}

QTabBar::tab {{
    background-color: transparent;
    color: #666666;
    padding: 6px 12px;
    border: none;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {colors["primary"]};
    border-bottom: 2px solid {colors["primary"]};
}}

QTabBar::tab:hover {{
    color: {colors["primary"]};
}}

QLineEdit {{
    padding: 6px;
    border: none;
    border-bottom: 1px solid #cccccc;
    background-color: {colors["background"]};
    color: {colors["text"]};
}}

QPushButton {{
    background-color: transparent;
    color: {colors["primary"]};
    padding: 6px 12px;
    border: 1px solid {colors["primary"]};
    border-radius: 4px;
}}

QPushButton:hover {{
    background-color: {colors["primary"]};
    color: white;
}}

QPushButton:pressed {{
    background-color: #3a76d8;
    color: white;
}}

QToolBar {{
    background-color: {colors["background"]};
    border: none;
    spacing: 6px;
    padding: 3px;
}}

QMenuBar {{
    background-color: {colors["background"]}; /* Background color from theme */
    color: #333333; /* Dark text for menu bar */
}}

QMenuBar::item {{
    spacing: 3px;
    padding: 6px 12px;
    
}}

QMenuBar::item:selected {{
    background: #f0f0f0; /* Highlight on hover/selection */
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: 4px;
    border-radius: 4px;
}}

QToolButton:hover {{
    background-color: #f0f0f0;
}}

QToolButton:pressed {{
    background-color: #e0e0e0;
}}

QMenu {{
    background-color: {colors["background"]};
    color: #333333; /* Ensure readability against light backgrounds */
    border: 1px solid #cccccc;
}}

QMenu::item {{
    padding: 6px 24px 6px 12px;
}}

QMenu::item:selected {{
    background-color: #f0f0f0;
    color: {colors["primary"]};
}}

QStatusBar {{
    background-color: {colors["background"]};
    color: #666666;
    border: none;
}}

QProgressBar {{
    border: none;
    border-radius: 2px;
    text-align: center;
    background-color: #f0f0f0;
}}

QProgressBar::chunk {{
    background-color: {colors["primary"]};
}}
"""
