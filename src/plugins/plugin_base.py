#!/usr/bin/env python3
# NebulaFusion Browser - Plugin Base

import os
import sys
from PyQt6.QtCore import QObject

class PluginBase(QObject):
    """
    Base class for browser plugins.
    All plugins must inherit from this class.
    """
    
    def __init__(self, api):
        """Initialize the plugin."""
        super().__init__()
        self.api = api
        self.plugin_id = api.plugin_id
        self.manifest = api.manifest
    
    def activate(self):
        """
        Activate the plugin.
        Called when the plugin is enabled.
        
        Returns:
            bool: True if activation was successful, False otherwise.
        """
        return True
    
    def deactivate(self):
        """
        Deactivate the plugin.
        Called when the plugin is disabled.
        
        Returns:
            bool: True if deactivation was successful, False otherwise.
        """
        return True
    
    def configure(self):
        """
        Configure the plugin.
        Called when the user wants to configure the plugin.
        """
        pass
    
    def get_name(self):
        """Get the plugin name."""
        return self.manifest.get("name", "Unknown Plugin")
    
    def get_version(self):
        """Get the plugin version."""
        return self.manifest.get("version", "0.0.0")
    
    def get_author(self):
        """Get the plugin author."""
        return self.manifest.get("author", "Unknown Author")
    
    def get_description(self):
        """Get the plugin description."""
        return self.manifest.get("description", "No description available.")
    
    def get_permissions(self):
        """Get the plugin permissions."""
        return self.manifest.get("permissions", [])
    
    def has_permission(self, permission):
        """Check if the plugin has a permission."""
        return permission in self.get_permissions()
