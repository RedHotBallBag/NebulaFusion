#!/usr/bin/env python3
# NebulaFusion Browser - Test Theming System

import os
import sys
import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import browser modules
from src.core.application import Application
from src.themes.theme_manager import ThemeManager

class TestThemingSystem(unittest.TestCase):
    """Test cases for the theming system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment."""
        # Create application
        cls.app = QApplication.instance() or QApplication(sys.argv)
        
        # Create browser application
        cls.browser = Application()
        
        # Initialize browser
        cls.browser.initialize()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        # Clean up browser
        cls.browser.cleanup()
    
    def test_theme_manager(self):
        """Test theme manager."""
        # Get theme manager
        theme_manager = self.browser.theme_manager
        
        # Check if theme manager is initialized
        self.assertTrue(hasattr(theme_manager, "available_themes"))
        
        # Check if default themes are available
        self.assertIn("Default", theme_manager.available_themes)
        self.assertIn("Dark", theme_manager.available_themes)
        self.assertIn("Light", theme_manager.available_themes)
        self.assertIn("Neon", theme_manager.available_themes)
        self.assertIn("Minimal", theme_manager.available_themes)
        
        # Get current theme
        current_theme = theme_manager.get_current_theme()
        
        # Check if current theme is valid
        self.assertIsNotNone(current_theme)
        
        # Apply a different theme
        original_theme = theme_manager.current_theme
        
        if original_theme != "Dark":
            theme_manager.apply_theme("Dark")
            self.assertEqual(theme_manager.current_theme, "Dark")
        else:
            theme_manager.apply_theme("Light")
            self.assertEqual(theme_manager.current_theme, "Light")
        
        # Restore original theme
        theme_manager.apply_theme(original_theme)
        self.assertEqual(theme_manager.current_theme, original_theme)
    
    def test_theme_creation(self):
        """Test theme creation."""
        # Get theme manager
        theme_manager = self.browser.theme_manager
        
        # Create a test theme
        test_theme = {
            "name": "Test Theme",
            "description": "A test theme for NebulaFusion browser.",
            "author": "Test Author",
            "version": "1.0.0",
            "dark": False,
            "stylesheet": """
            /* Test Theme for NebulaFusion Browser */
            QMainWindow {
                background-color: #F0F0F0;
                color: #333333;
            }
            """,
            "colors": {
                "primary": "#3498DB",
                "secondary": "#2ECC71",
                "accent": "#F1C40F",
                "background": "#F0F0F0",
                "foreground": "#333333",
                "surface": "#FFFFFF",
                "error": "#E74C3C",
                "warning": "#F39C12",
                "success": "#2ECC71",
                "info": "#3498DB"
            }
        }
        
        # Create theme
        success = theme_manager.create_theme(test_theme, save=False)
        
        # Check if theme was created
        self.assertTrue(success)
        self.assertIn("Test Theme", theme_manager.available_themes)
        
        # Get theme
        theme = theme_manager.get_theme("Test Theme")
        
        # Check theme properties
        self.assertEqual(theme["name"], "Test Theme")
        self.assertEqual(theme["description"], "A test theme for NebulaFusion browser.")
        self.assertEqual(theme["author"], "Test Author")
        self.assertEqual(theme["version"], "1.0.0")
        self.assertEqual(theme["dark"], False)
        self.assertIn("stylesheet", theme)
        self.assertIn("colors", theme)
        
        # Apply theme
        original_theme = theme_manager.current_theme
        success = theme_manager.apply_theme("Test Theme")
        
        # Check if theme was applied
        self.assertTrue(success)
        self.assertEqual(theme_manager.current_theme, "Test Theme")
        
        # Restore original theme
        theme_manager.apply_theme(original_theme)
        
        # Delete theme
        del theme_manager.available_themes["Test Theme"]
    
    def test_dark_mode_toggle(self):
        """Test dark mode toggle."""
        # Get theme manager
        theme_manager = self.browser.theme_manager
        
        # Get original theme
        original_theme = theme_manager.current_theme
        original_dark_mode = theme_manager.is_dark_mode()
        
        # Toggle dark mode
        theme_manager.toggle_dark_mode()
        
        # Check if dark mode was toggled
        self.assertNotEqual(theme_manager.is_dark_mode(), original_dark_mode)
        
        # Toggle dark mode again
        theme_manager.toggle_dark_mode()
        
        # Check if dark mode was toggled back
        self.assertEqual(theme_manager.is_dark_mode(), original_dark_mode)
        
        # Restore original theme
        theme_manager.apply_theme(original_theme)

if __name__ == "__main__":
    unittest.main()
