#!/usr/bin/env python3
# NebulaFusion Browser - Plugin Loader

import os
import sys
import importlib.util
import json
import inspect
from PyQt6.QtCore import QObject, pyqtSignal

class PluginLoader(QObject):
    """
    Loader for browser plugins.
    Handles loading, validating, and initializing plugins.
    """
    
    # Signals
    plugin_loaded = pyqtSignal(str, object)  # plugin_id, plugin_instance
    plugin_unloaded = pyqtSignal(str)  # plugin_id
    plugin_error = pyqtSignal(str, str)  # plugin_id, error_message
    
    def __init__(self, app_controller):
        """Initialize the plugin loader."""
        super().__init__()
        self.app_controller = app_controller
        
        # Loaded plugins
        self.loaded_plugins = {}
        
        # Plugin base class
        self.plugin_base_class = None
    
    def initialize(self):
        """Initialize the plugin loader."""
        self.app_controller.logger.info("Initializing plugin loader...")
        
        # Import plugin base class
        from src.plugins.plugin_base import PluginBase
        self.plugin_base_class = PluginBase
        
        self.app_controller.logger.info("Plugin loader initialized.")
    
    def load_plugin(self, plugin_path):
        """Load a plugin from a path."""
        plugin_id = None
        try:
            self.app_controller.logger.info(f"Loading plugin from: {plugin_path}")
            
            # Check if path exists
            if not os.path.exists(plugin_path):
                raise FileNotFoundError(f"Plugin path not found: {plugin_path}")
            
            # Check if path is a directory
            if not os.path.isdir(plugin_path):
                raise NotADirectoryError(f"Plugin path is not a directory: {plugin_path}")
            
            # Check if __init__.py exists
            init_path = os.path.join(plugin_path, "__init__.py")
            if not os.path.exists(init_path):
                raise FileNotFoundError(f"Plugin __init__.py not found: {init_path}")
            
            # Check if manifest.json exists
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if not os.path.exists(manifest_path):
                raise FileNotFoundError(f"Plugin manifest.json not found: {manifest_path}")
            
            # Load and validate manifest
            self.app_controller.logger.info(f"Loading manifest from: {manifest_path}")
            with open(manifest_path, "r", encoding='utf-8') as f:
                manifest = json.load(f)
            
            self._validate_manifest(manifest)
            plugin_id = manifest["id"]
            self.app_controller.logger.info(f"Plugin ID: {plugin_id}")
            
            # Check if plugin is already loaded
            if plugin_id in self.loaded_plugins:
                self.app_controller.logger.warning(f"Plugin already loaded: {plugin_id}")
                return plugin_id
            
            # Add plugin directory to Python path
            plugin_dir = os.path.dirname(plugin_path)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            # Load plugin module
            plugin_name = os.path.basename(plugin_path)
            self.app_controller.logger.info(f"Importing plugin module: {plugin_name}")
            
            spec = importlib.util.spec_from_file_location(plugin_name, init_path)
            if spec is None:
                raise ImportError(f"Could not load spec for plugin: {plugin_name}")
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            
            try:
                spec.loader.exec_module(module)
            except Exception as e:
                raise ImportError(f"Error executing module {plugin_name}: {str(e)}")
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, self.plugin_base_class) and 
                    obj != self.plugin_base_class):
                    plugin_class = obj
                    break
            
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")
            
            # Create plugin API
            from src.plugins.plugin_api import PluginAPI
            plugin_api = PluginAPI(self.app_controller, plugin_id, manifest)
            
            # Create plugin instance
            self.app_controller.logger.info(f"Creating instance of plugin: {plugin_id}")
            plugin_instance = plugin_class(plugin_api)
            
            # Store plugin
            self.loaded_plugins[plugin_id] = {
                "id": plugin_id,
                "name": manifest.get("name", "Unnamed Plugin"),
                "version": manifest.get("version", "1.0.0"),
                "author": manifest.get("author", "Unknown"),
                "description": manifest.get("description", "No description provided"),
                "permissions": manifest.get("permissions", []),
                "path": plugin_path,
                "manifest": manifest,
                "instance": plugin_instance,
                "api": plugin_api,
                "enabled": False
            }
            
            # Emit signal
            self.plugin_loaded.emit(plugin_id, plugin_instance)
            self.app_controller.logger.info(f"Successfully loaded plugin: {plugin_id}")
            
            return plugin_id
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in manifest: {str(e)}"
            self.app_controller.logger.error(error_msg, exc_info=True)
            if plugin_id:
                self.plugin_error.emit(plugin_id, error_msg)
            return None
            
        except ImportError as e:
            error_msg = f"Import error loading plugin: {str(e)}"
            self.app_controller.logger.error(error_msg, exc_info=True)
            if plugin_id:
                self.plugin_error.emit(plugin_id, error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Error loading plugin: {str(e)}"
            self.app_controller.logger.error(error_msg, exc_info=True)
            if plugin_id:
                self.plugin_error.emit(plugin_id, error_msg)
            return None
    
    def unload_plugin(self, plugin_id):
        """Unload a plugin."""
        try:
            # Check if plugin is loaded
            if plugin_id not in self.loaded_plugins:
                raise ValueError(f"Plugin not loaded: {plugin_id}")
            
            # Get plugin
            plugin = self.loaded_plugins[plugin_id]
            
            # Deactivate plugin if enabled
            if plugin["enabled"]:
                self.deactivate_plugin(plugin_id)
            
            # Remove plugin
            del self.loaded_plugins[plugin_id]
            
            # Emit signal
            self.plugin_unloaded.emit(plugin_id)
            
            self.app_controller.logger.info(f"Plugin unloaded: {plugin_id}")
            
            return True
        
        except Exception as e:
            error_message = f"Error unloading plugin: {str(e)}"
            self.app_controller.logger.error(error_message)
            
            # Emit signal
            self.plugin_error.emit(plugin_id, error_message)
            
            return False
    
    def activate_plugin(self, plugin_id):
        """Activate a plugin."""
        try:
            # Check if plugin is loaded
            if plugin_id not in self.loaded_plugins:
                raise ValueError(f"Plugin not loaded: {plugin_id}")
            
            # Get plugin
            plugin = self.loaded_plugins[plugin_id]
            
            # Check if plugin is already enabled
            if plugin["enabled"]:
                return True
            
            # Activate plugin
            success = plugin["instance"].activate()
            
            if success:
                # Update plugin status
                plugin["enabled"] = True
                
                self.app_controller.logger.info(f"Plugin activated: {plugin_id}")
            else:
                error_message = f"Plugin activation failed: {plugin_id}"
                self.app_controller.logger.error(error_message)
                
                # Emit signal
                self.plugin_error.emit(plugin_id, error_message)
            
            return success
        
        except Exception as e:
            error_message = f"Error activating plugin: {str(e)}"
            self.app_controller.logger.error(error_message)
            
            # Emit signal
            self.plugin_error.emit(plugin_id, error_message)
            
            return False
    
    def deactivate_plugin(self, plugin_id):
        """Deactivate a plugin."""
        try:
            # Check if plugin is loaded
            if plugin_id not in self.loaded_plugins:
                raise ValueError(f"Plugin not loaded: {plugin_id}")
            
            # Get plugin
            plugin = self.loaded_plugins[plugin_id]
            
            # Check if plugin is enabled
            if not plugin["enabled"]:
                return True
            
            # Deactivate plugin
            success = plugin["instance"].deactivate()
            
            if success:
                # Update plugin status
                plugin["enabled"] = False
                
                self.app_controller.logger.info(f"Plugin deactivated: {plugin_id}")
            else:
                error_message = f"Plugin deactivation failed: {plugin_id}"
                self.app_controller.logger.error(error_message)
                
                # Emit signal
                self.plugin_error.emit(plugin_id, error_message)
            
            return success
        
        except Exception as e:
            error_message = f"Error deactivating plugin: {str(e)}"
            self.app_controller.logger.error(error_message)
            
            # Emit signal
            self.plugin_error.emit(plugin_id, error_message)
            
            return False
    
    def reload_plugin(self, plugin_id):
        """Reload a plugin."""
        try:
            # Check if plugin is loaded
            if plugin_id not in self.loaded_plugins:
                raise ValueError(f"Plugin not loaded: {plugin_id}")
            
            # Get plugin
            plugin = self.loaded_plugins[plugin_id]
            
            # Get plugin path
            plugin_path = plugin["path"]
            
            # Check if plugin is enabled
            was_enabled = plugin["enabled"]
            
            # Unload plugin
            self.unload_plugin(plugin_id)
            
            # Load plugin
            new_plugin_id = self.load_plugin(plugin_path)
            
            if new_plugin_id and was_enabled:
                # Activate plugin
                self.activate_plugin(new_plugin_id)
            
            self.app_controller.logger.info(f"Plugin reloaded: {plugin_id}")
            
            return new_plugin_id is not None
        
        except Exception as e:
            error_message = f"Error reloading plugin: {str(e)}"
            self.app_controller.logger.error(error_message)
            
            # Emit signal
            self.plugin_error.emit(plugin_id, error_message)
            
            return False
    
    def get_plugin(self, plugin_id):
        """Get a plugin by ID."""
        return self.loaded_plugins.get(plugin_id)
    
    def get_plugins(self):
        """Get all loaded plugins."""
        return self.loaded_plugins
    
    def _validate_manifest(self, manifest):
        """
        Validate a plugin manifest.
        
        Args:
            manifest (dict): The plugin manifest to validate
            
        Raises:
            ValueError: If the manifest is invalid
        """
        # Check required fields
        required_fields = ["id", "name", "version", "author", "description"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field in manifest: {field}")
        
        # Validate ID
        if not isinstance(manifest["id"], str) or not manifest["id"]:
            raise ValueError("Plugin ID must be a non-empty string")
            
        # Validate name
        if not isinstance(manifest["name"], str) or not manifest["name"]:
            raise ValueError("Plugin name must be a non-empty string")
            
        # Validate version
        if not isinstance(manifest["version"], str) or not manifest["version"]:
            raise ValueError("Plugin version must be a non-empty string")
            
        # Validate author
        if not isinstance(manifest["author"], str) or not manifest["author"]:
            raise ValueError("Plugin author must be a non-empty string")
            
        # Validate description
        if not isinstance(manifest["description"], str):
            raise ValueError("Plugin description must be a string")
        
        # Validate permissions if present
        if "permissions" in manifest:
            if not isinstance(manifest["permissions"], list):
                raise ValueError("Plugin permissions must be a list")
            
            # Define valid permissions
            valid_permissions = [
                "tabs", "bookmarks", "history", "downloads", "cookies", "storage",
                "webRequest", "notifications", "contextMenus", "clipboardRead", 
                "clipboardWrite", "toolbar"  # Added toolbar permission
            ]
            
            for permission in manifest["permissions"]:
                if not isinstance(permission, str):
                    raise ValueError("Permission must be a string")
                if permission not in valid_permissions:
                    raise ValueError(f"Invalid permission: {permission}")
