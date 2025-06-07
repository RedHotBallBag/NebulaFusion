#!/usr/bin/env python3
# NebulaFusion Browser - Plugin Manager

import os
import sys
import shutil
import zipfile
import tempfile
from PyQt6.QtCore import QObject, pyqtSignal
import json


class PluginManager(QObject):
    """
    Manager for browser plugins.
    Handles plugin installation, removal, and management.
    """

    # Signals
    plugin_enabled = pyqtSignal(str)  # plugin_id
    plugin_disabled = pyqtSignal(str)  # plugin_id
    plugin_installed = pyqtSignal(str)  # plugin_id
    plugin_uninstalled = pyqtSignal(str)  # plugin_id
    plugin_configured = pyqtSignal(str)  # plugin_id

    def __init__(self, app_controller):
        """Initialize the plugin manager."""
        super().__init__()
        self.app_controller = app_controller

        # Plugin directories
        self.plugin_dirs = []

        # Default plugin directory
        self.default_plugin_dir = os.path.expanduser("~/.nebulafusion/plugins")

        # Store plugins
        self.store_plugins = []

        # Track loaded plugins
        self._loaded_plugins = {}

    def initialize(self):
        """Initialize the plugin manager."""
        self.app_controller.logger.info("Initializing plugin manager...")

        # Create default plugin directory if it doesn't exist
        os.makedirs(self.default_plugin_dir, exist_ok=True)

        # Add default plugin directory
        self.plugin_dirs.append(self.default_plugin_dir)

        # Add built-in plugin directory
        built_in_plugin_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "plugins",
            "sample_plugins",
        )
        if os.path.exists(built_in_plugin_dir):
            self.plugin_dirs.append(built_in_plugin_dir)

        # Add src/plugins directory
        src_plugins_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins"
        )
        self.plugin_dirs.append(src_plugins_dir)

        # Load plugins
        self._load_plugins()

        # Load store plugins
        self._load_store_plugins()

        self.app_controller.logger.info("Plugin manager initialized.")

    def _load_plugins(self):
        """Load plugins from plugin directories."""
        self.app_controller.logger.info("Loading plugins...")
        plugin_loader = self.app_controller.plugin_loader
        loaded_plugin_ids = (
            set()
        )  # Keep track of IDs loaded in this session to avoid conflicts

        for plugin_dir_root in self.plugin_dirs:
            if not os.path.exists(plugin_dir_root):
                self.app_controller.logger.warning(
                    f"Plugin directory root not found: {plugin_dir_root}"
                )
                continue

            self.app_controller.logger.info(
                f"Scanning plugin directory: {plugin_dir_root}"
            )

            # Get all subdirectories that might be plugins
            potential_plugins = [
                os.path.join(plugin_dir_root, d)
                for d in os.listdir(plugin_dir_root)
                if os.path.isdir(os.path.join(plugin_dir_root, d))
            ]

            # Also check the root directory for direct plugin files
            potential_plugins.append(plugin_dir_root)

            for potential_plugin_path in potential_plugins:
                # Check for manifest.json to get plugin_id
                manifest_path = os.path.join(potential_plugin_path, "manifest.json")
                init_path = os.path.join(potential_plugin_path, "__init__.py")

                self.app_controller.logger.debug(
                    f"Checking potential plugin at: {potential_plugin_path}"
                )

                if os.path.exists(manifest_path) and os.path.exists(init_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                        plugin_id = manifest.get("id")

                        if not plugin_id:
                            self.app_controller.logger.warning(
                                f"Plugin at {potential_plugin_path} has no ID in manifest"
                            )
                            continue

                        self.app_controller.logger.info(
                            f"Found plugin: {plugin_id} at {potential_plugin_path}"
                        )

                        if plugin_id not in loaded_plugin_ids:
                            actual_plugin_id_loaded = plugin_loader.load_plugin(
                                potential_plugin_path
                            )
                            if (
                                actual_plugin_id_loaded
                            ):  # load_plugin returns ID on success
                                loaded_plugin_ids.add(actual_plugin_id_loaded)
                                self.app_controller.logger.info(
                                    f"Successfully loaded plugin: {plugin_id}"
                                )
                            else:
                                self.app_controller.logger.error(
                                    f"Failed to load plugin: {plugin_id}"
                                )
                        else:
                            self.app_controller.logger.info(
                                f"Plugin '{plugin_id}' already processed in this session. Skipping {potential_plugin_path}"
                            )

                    except json.JSONDecodeError as e:
                        self.app_controller.logger.error(
                            f"Could not decode manifest.json in {potential_plugin_path}: {str(e)}"
                        )
                    except Exception as e:
                        self.app_controller.logger.error(
                            f"Error loading plugin at {potential_plugin_path}: {str(e)}",
                            exc_info=True,
                        )

    def _load_store_plugins(self):
        """Load store plugins."""
        # TODO: Implement loading store plugins from a remote source
        # For now, we'll just use a hardcoded list
        self.store_plugins = []

    def get_plugin(self, plugin_id):
        """Get a plugin by ID."""
        return self.app_controller.plugin_loader.get_plugin(plugin_id)

    def get_plugins(self):
        """
        Get all loaded plugins.

        Returns:
            dict: A dictionary of all loaded plugins with plugin IDs as keys
        """
        return self.app_controller.plugin_loader.get_plugins()

    def get_available_plugins(self):
        """
        Get all available plugins (loaded and not loaded).

        Returns:
            dict: A dictionary of all available plugins with plugin IDs as keys
        """
        # For now, return the same as get_plugins
        return self.get_plugins()

    def get_store_plugins(self):
        """
        Get all available plugins from the store.

        Returns:
            list: A list of available plugins from the store
        """
        return self.store_plugins

    def configure_plugin(self, plugin_id):
        """
        Configure a plugin.

        Args:
            plugin_id (str): The ID of the plugin to configure

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        try:
            # Get the plugin
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                self.app_controller.logger.error(f"Plugin not found: {plugin_id}")
                return False

            # Check if plugin has a configuration dialog
            if hasattr(plugin, "show_config_dialog"):
                plugin.show_config_dialog()
                return True
            else:
                # Show a message that the plugin has no configuration
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.information(
                    None,
                    "Plugin Configuration",
                    f"The plugin '{plugin_id}' has no configuration options.",
                )
                return True

        except Exception as e:
            self.app_controller.logger.error(
                f"Error configuring plugin {plugin_id}: {str(e)}"
            )
            return False

    def enable_plugin(self, plugin_id):
        """Enable a plugin."""
        try:
            plugin_loader = self.app_controller.plugin_loader
            success = plugin_loader.activate_plugin(plugin_id)
            if success:
                self.plugin_enabled.emit(plugin_id)
            return success
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self.app_controller.logger.error(
                f"Error enabling plugin {plugin_id}: {e}\n{tb}"
            )
            return False

    def disable_plugin(self, plugin_id):
        """Disable a plugin."""
        try:
            plugin_loader = self.app_controller.plugin_loader
            success = plugin_loader.deactivate_plugin(plugin_id)
            if success:
                self.plugin_disabled.emit(plugin_id)
            return success
        except Exception as e:
            import traceback

            tb = traceback.format_exc()
            self.app_controller.logger.error(
                f"Error disabling plugin {plugin_id}: {e}\n{tb}"
            )
            return False

    def install_plugin(self, plugin_path):
        """Install a plugin from a file."""
        try:
            # Check if file exists
            if not os.path.exists(plugin_path):
                raise FileNotFoundError(f"Plugin file not found: {plugin_path}")

            # Create temporary directory
            temp_dir = tempfile.mkdtemp()

            # Extract plugin
            if plugin_path.endswith(".zip"):
                # Extract ZIP file
                with zipfile.ZipFile(plugin_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                # Copy file
                shutil.copy(plugin_path, temp_dir)

            # Find plugin directory
            plugin_dir = None
            for item in os.listdir(temp_dir):
                item_path = os.path.join(temp_dir, item)

                # Check if item is a directory
                if os.path.isdir(item_path):
                    # Check if directory contains manifest.json
                    manifest_path = os.path.join(item_path, "manifest.json")
                    if os.path.exists(manifest_path):
                        plugin_dir = item_path
                        break

            if not plugin_dir:
                # Check if temp_dir itself contains manifest.json
                manifest_path = os.path.join(temp_dir, "manifest.json")
                if os.path.exists(manifest_path):
                    plugin_dir = temp_dir

            if not plugin_dir:
                raise FileNotFoundError("Plugin manifest.json not found in archive")

            # Load plugin
            plugin_id = self.app_controller.plugin_loader.load_plugin(plugin_dir)

            if not plugin_id:
                raise ValueError("Failed to load plugin")

            # Get plugin
            plugin = self.app_controller.plugin_loader.get_plugin(plugin_id)

            # Install plugin to default plugin directory
            plugin_install_dir = os.path.join(self.default_plugin_dir, plugin_id)

            # Remove existing plugin if it exists
            if os.path.exists(plugin_install_dir):
                shutil.rmtree(plugin_install_dir)

            # Create plugin directory
            os.makedirs(plugin_install_dir, exist_ok=True)

            # Copy plugin files
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                dest_path = os.path.join(plugin_install_dir, item)

                if os.path.isdir(item_path):
                    shutil.copytree(item_path, dest_path)
                else:
                    shutil.copy2(item_path, dest_path)

            # Clean up
            shutil.rmtree(temp_dir)

            # Emit signal
            self.plugin_installed.emit(plugin_id)

            self.app_controller.logger.info(f"Plugin installed: {plugin_id}")

            return True

        except Exception as e:
            error_message = f"Error installing plugin: {str(e)}"
            self.app_controller.logger.error(error_message)
            return False

    def uninstall_plugin(self, plugin_id):
        """Uninstall a plugin."""
        try:
            # Get plugin
            plugin = self.app_controller.plugin_loader.get_plugin(plugin_id)
            if not plugin:
                raise ValueError(f"Plugin not found: {plugin_id}")

            # Get plugin path
            plugin_path = plugin.get("path")
            if not plugin_path:
                raise ValueError(f"Plugin path not found for: {plugin_id}")

            # Check if plugin is in default plugin directory
            if not plugin_path.startswith(self.default_plugin_dir):
                raise ValueError(f"Cannot uninstall built-in plugin: {plugin_id}")

            # Unload plugin first
            self.app_controller.logger.info(f"Unloading plugin: {plugin_id}")
            self.app_controller.plugin_loader.unload_plugin(plugin_id)

            # Remove plugin directory
            self.app_controller.logger.info(f"Removing plugin directory: {plugin_path}")
            if os.path.exists(plugin_path):
                import shutil

                shutil.rmtree(plugin_path)

            self.app_controller.logger.info(
                f"Successfully uninstalled plugin: {plugin_id}"
            )
            self.plugin_uninstalled.emit(plugin_id)
            return True

        except Exception as e:
            self.app_controller.logger.error(
                f"Error uninstalling plugin {plugin_id}: {str(e)}", exc_info=True
            )
            return False

        # TODO: Implement downloading and installing store plugins
        # For now, we'll just pretend it worked
        self.app_controller.logger.info(f"Plugin installed from store: {plugin_id}")

        # Emit signal
        self.plugin_installed.emit(plugin_id)

        return True

    def create_plugin_template(self, directory):
        """Create a plugin template in a directory."""
        try:
            # Create plugin directory
            os.makedirs(directory, exist_ok=True)

            # Create __init__.py
            with open(os.path.join(directory, "__init__.py"), "w") as f:
                f.write(
                    """#!/usr/bin/env python3
# NebulaFusion Plugin Template

from src.plugins.plugin_base import PluginBase

class Plugin(PluginBase):
    \"\"\"
    Template plugin for NebulaFusion browser.
    \"\"\"
    
    def __init__(self, api):
        \"\"\"Initialize the plugin.\"\"\"
        super().__init__(api)
        
        # Plugin state
        self.initialized = False
    
    def activate(self):
        \"\"\"Activate the plugin.\"\"\"
        # Register hooks
        self.api.hooks.register_hook("onBrowserStart", self.plugin_id, self.on_browser_start)
        self.api.hooks.register_hook("onBrowserExit", self.plugin_id, self.on_browser_exit)
        
        # Initialize plugin
        self.initialized = True
        
        return True
    
    def deactivate(self):
        \"\"\"Deactivate the plugin.\"\"\"
        # Unregister hooks
        self.api.hooks.unregister_all_hooks(self.plugin_id)
        
        # Clean up
        self.initialized = False
        
        return True
    
    def configure(self):
        \"\"\"Configure the plugin.\"\"\"
        # Show configuration dialog
        self.api.ui.show_message("Plugin Configuration", "This is a template plugin.")
    
    def on_browser_start(self):
        \"\"\"Handle browser start event.\"\"\"
        self.api.logger.info("Browser started")
    
    def on_browser_exit(self):
        \"\"\"Handle browser exit event.\"\"\"
        self.api.logger.info("Browser exiting")
"""
                )

            # Create manifest.json
            with open(os.path.join(directory, "manifest.json"), "w") as f:
                f.write(
                    """{
    "id": "template_plugin",
    "name": "Template Plugin",
    "version": "1.0.0",
    "author": "Your Name",
    "description": "A template plugin for NebulaFusion browser.",
    "permissions": [
        "tabs",
        "bookmarks",
        "history"
    ]
}"""
                )

            # Create README.md
            with open(os.path.join(directory, "README.md"), "w") as f:
                f.write(
                    """# Template Plugin

A template plugin for NebulaFusion browser.

## Features

- Basic plugin structure
- Hook registration
- Plugin lifecycle management

## Installation

1. Copy this directory to the NebulaFusion plugins directory
2. Enable the plugin in the browser settings

## Development

This template provides a starting point for developing NebulaFusion plugins.
Customize it to add your own features and functionality.

## License

MIT
"""
                )

            self.app_controller.logger.info(f"Plugin template created in {directory}")

            return True

        except Exception as e:
            error_message = f"Error creating plugin template: {str(e)}"
            self.app_controller.logger.error(error_message)
            return False
