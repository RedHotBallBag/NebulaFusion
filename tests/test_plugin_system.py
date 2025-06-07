#!/usr/bin/env python3
# NebulaFusion Browser - Test Plugin System

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
from src.plugins.plugin_loader import PluginLoader
from src.plugins.plugin_manager import PluginManager
from src.plugins.hook_registry import HookRegistry
from src.plugins.plugin_api import PluginAPI
from src.plugins.plugin_base import PluginBase

class TestPluginSystem(unittest.TestCase):
    """Test cases for the plugin system."""
    
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
    
    def test_plugin_loader(self):
        """Test plugin loader."""
        # Get plugin loader
        plugin_loader = self.browser.plugin_loader
        
        # Check if plugin loader is initialized
        self.assertTrue(hasattr(plugin_loader, "loaded_plugins"))
        
        # Get sample plugin path
        sample_plugin_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "plugins", "sample_plugins", "sample_plugin"
        )
        
        # Check if sample plugin exists
        self.assertTrue(os.path.exists(sample_plugin_path))
        
        # Load sample plugin
        plugin_id = plugin_loader.load_plugin(sample_plugin_path)
        
        # Check if plugin was loaded
        self.assertIsNotNone(plugin_id)
        self.assertIn(plugin_id, plugin_loader.loaded_plugins)
        
        # Get plugin
        plugin = plugin_loader.get_plugin(plugin_id)
        
        # Check plugin properties
        self.assertEqual(plugin["id"], "sample_plugin")
        self.assertEqual(plugin["name"], "Sample Plugin")
        self.assertEqual(plugin["version"], "1.0.0")
        self.assertEqual(plugin["author"], "NebulaFusion Team")
        
        # Activate plugin
        success = plugin_loader.activate_plugin(plugin_id)
        
        # Check if plugin was activated
        self.assertTrue(success)
        self.assertTrue(plugin_loader.loaded_plugins[plugin_id]["enabled"])
        
        # Deactivate plugin
        success = plugin_loader.deactivate_plugin(plugin_id)
        
        # Check if plugin was deactivated
        self.assertTrue(success)
        self.assertFalse(plugin_loader.loaded_plugins[plugin_id]["enabled"])
        
        # Unload plugin
        success = plugin_loader.unload_plugin(plugin_id)
        
        # Check if plugin was unloaded
        self.assertTrue(success)
        self.assertNotIn(plugin_id, plugin_loader.loaded_plugins)
    
    def test_hook_registry(self):
        """Test hook registry."""
        # Get hook registry
        hook_registry = self.browser.hook_registry
        
        # Check if hook registry is initialized
        self.assertTrue(hasattr(hook_registry, "hooks"))
        
        # Check if hooks are initialized
        for hook_name in hook_registry.available_hooks:
            self.assertIn(hook_name, hook_registry.hooks)
        
        # Create a test hook
        hook_name = "onTestHook"
        plugin_id = "test_plugin"
        
        # Create a callback function
        callback_called = [False]
        def callback(*args):
            callback_called[0] = True
        
        # Register hook
        success = hook_registry.register_hook(hook_name, plugin_id, callback)
        
        # Check if hook was registered
        self.assertTrue(success)
        self.assertIn(plugin_id, hook_registry.hooks[hook_name])
        
        # Trigger hook
        hook_registry.trigger_hook(hook_name)
        
        # Check if callback was called
        self.assertTrue(callback_called[0])
        
        # Unregister hook
        success = hook_registry.unregister_hook(hook_name, plugin_id)
        
        # Check if hook was unregistered
        self.assertTrue(success)
        self.assertNotIn(plugin_id, hook_registry.hooks[hook_name])
    
    def test_plugin_api(self):
        """Test plugin API."""
        # Create a test manifest
        manifest = {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "author": "Test Author",
            "description": "Test Description",
            "permissions": ["tabs", "bookmarks", "history"]
        }
        
        # Create plugin API
        plugin_api = PluginAPI(self.browser, "test_plugin", manifest)
        
        # Check if API components are initialized
        self.assertIsNotNone(plugin_api.logger)
        self.assertIsNotNone(plugin_api.hooks)
        self.assertIsNotNone(plugin_api.tabs)
        self.assertIsNotNone(plugin_api.bookmarks)
        self.assertIsNotNone(plugin_api.history)
        self.assertIsNotNone(plugin_api.downloads)
        self.assertIsNotNone(plugin_api.cookies)
        self.assertIsNotNone(plugin_api.storage)
        self.assertIsNotNone(plugin_api.ui)
        self.assertIsNotNone(plugin_api.network)
        self.assertIsNotNone(plugin_api.filesystem)
        self.assertIsNotNone(plugin_api.settings)
        
        # Check if unique feature APIs are initialized
        self.assertIsNotNone(plugin_api.reality)
        self.assertIsNotNone(plugin_api.collaboration)
        self.assertIsNotNone(plugin_api.transformation)
        self.assertIsNotNone(plugin_api.timetravel)
        self.assertIsNotNone(plugin_api.dimensions)
        self.assertIsNotNone(plugin_api.voice)
        
        # Check permission checking
        self.assertTrue(plugin_api.has_permission("tabs"))
        self.assertTrue(plugin_api.has_permission("bookmarks"))
        self.assertTrue(plugin_api.has_permission("history"))
        self.assertFalse(plugin_api.has_permission("cookies"))
    
    def test_plugin_base(self):
        """Test plugin base class."""
        # Create a test manifest
        manifest = {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "author": "Test Author",
            "description": "Test Description",
            "permissions": ["tabs", "bookmarks", "history"]
        }
        
        # Create plugin API
        plugin_api = PluginAPI(self.browser, "test_plugin", manifest)
        
        # Create plugin instance
        plugin = PluginBase(plugin_api)
        
        # Check plugin properties
        self.assertEqual(plugin.plugin_id, "test_plugin")
        self.assertEqual(plugin.manifest, manifest)
        
        # Check plugin methods
        self.assertTrue(plugin.activate())
        self.assertTrue(plugin.deactivate())
        plugin.configure()  # Should not raise an exception
        
        # Check plugin getters
        self.assertEqual(plugin.get_name(), "Test Plugin")
        self.assertEqual(plugin.get_version(), "1.0.0")
        self.assertEqual(plugin.get_author(), "Test Author")
        self.assertEqual(plugin.get_description(), "Test Description")
        self.assertEqual(plugin.get_permissions(), ["tabs", "bookmarks", "history"])
        
        # Check permission checking
        self.assertTrue(plugin.has_permission("tabs"))
        self.assertTrue(plugin.has_permission("bookmarks"))
        self.assertTrue(plugin.has_permission("history"))
        self.assertFalse(plugin.has_permission("cookies"))
    
    def test_plugin_manager(self):
        """Test plugin manager."""
        # Get plugin manager
        plugin_manager = self.browser.plugin_manager
        
        # Check if plugin manager is initialized
        self.assertTrue(hasattr(plugin_manager, "plugin_dirs"))
        
        # Get plugins
        plugins = plugin_manager.get_plugins()
        
        # Check if plugins are returned
        self.assertIsInstance(plugins, list)
        
        # Get store plugins
        store_plugins = plugin_manager.get_store_plugins()
        
        # Check if store plugins are returned
        self.assertIsInstance(store_plugins, list)
        self.assertTrue(len(store_plugins) > 0)
        
        # Check if each store plugin has required fields
        for plugin in store_plugins:
            self.assertIn("id", plugin)
            self.assertIn("name", plugin)
            self.assertIn("version", plugin)
            self.assertIn("author", plugin)
            self.assertIn("description", plugin)
            self.assertIn("url", plugin)

if __name__ == "__main__":
    unittest.main()
