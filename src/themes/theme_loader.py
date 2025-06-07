#!/usr/bin/env python3
# NebulaFusion Browser - Theme Loader

import os
import sys
import json
from PyQt5.QtCore import QObject, pyqtSignal, QFile, QTextStream

class ThemeLoader(QObject):
    """
    Loads and parses theme files.
    """
    
    # Signals
    theme_loaded = pyqtSignal(str, dict)
    
    def __init__(self, app_controller):
        """Initialize the theme loader."""
        super().__init__()
        self.app_controller = app_controller
    
    def load_theme(self, theme_dir):
        """Load a theme from a directory."""
        try:
            # Check if theme.json exists
            theme_json = os.path.join(theme_dir, "theme.json")
            if not os.path.exists(theme_json):
                self.app_controller.logger.error(f"Theme.json not found in {theme_dir}")
                return None
            
            # Load theme.json
            with open(theme_json, 'r') as f:
                theme_info = json.load(f)
            
            # Check if style.qss exists
            style_file = os.path.join(theme_dir, "style.qss")
            if not os.path.exists(style_file):
                self.app_controller.logger.error(f"Style.qss not found in {theme_dir}")
                return None
            
            # Load style.qss
            with open(style_file, 'r') as f:
                style = f.read()
            
            # Create theme data
            theme_data = {
                "info": theme_info,
                "style": style,
                "dir": theme_dir
            }
            
            # Check for preview image
            preview_file = os.path.join(theme_dir, "preview.png")
            if os.path.exists(preview_file):
                theme_data["preview"] = preview_file
            
            # Emit signal
            theme_name = os.path.basename(theme_dir)
            self.theme_loaded.emit(theme_name, theme_data)
            
            return theme_data
        
        except Exception as e:
            self.app_controller.logger.error(f"Error loading theme from {theme_dir}: {e}")
            return None
    
    def parse_color_scheme(self, theme_info):
        """Parse color scheme from theme info."""
        color_scheme = theme_info.get("color_scheme", {})
        
        # Set default colors if missing
        if "primary" not in color_scheme:
            color_scheme["primary"] = "#4a86e8"
        if "secondary" not in color_scheme:
            color_scheme["secondary"] = "#f1c232"
        if "background" not in color_scheme:
            color_scheme["background"] = "#ffffff" if theme_info.get("type") == "light" else "#2d2d2d"
        if "text" not in color_scheme:
            color_scheme["text"] = "#333333" if theme_info.get("type") == "light" else "#ffffff"
        if "accent" not in color_scheme:
            color_scheme["accent"] = "#6aa84f"
        
        return color_scheme
    
    def generate_preview(self, theme_data):
        """Generate a preview image for a theme."""
        # This would typically generate a preview image
        # For now, just return a placeholder
        return os.path.join(theme_data["dir"], "preview.png")
