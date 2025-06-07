#!/usr/bin/env python3
# NebulaFusion Plugin Template

from src.plugins.plugin_base import PluginBase

class Plugin(PluginBase):
    """
    Template plugin for NebulaFusion browser.
    """
    
    def __init__(self, api):
        """Initialize the plugin."""
        super().__init__(api)
        
        # Plugin state
        self.initialized = False
    
    def activate(self):
        """Activate the plugin."""
        # Register hooks
        self.api.hooks.register_hook("onBrowserStart", self.plugin_id, self.on_browser_start)
        self.api.hooks.register_hook("onBrowserExit", self.plugin_id, self.on_browser_exit)
        
        # Initialize plugin
        self.initialized = True
        
        return True
    
    def deactivate(self):
        """Deactivate the plugin."""
        # Unregister hooks
        self.api.hooks.unregister_all_hooks(self.plugin_id)
        
        # Clean up
        self.initialized = False
        
        return True
    
    def configure(self):
        """Configure the plugin."""
        # Show configuration dialog
        self.api.ui.show_message("Plugin Configuration", "This is a template plugin.")
    
    def on_browser_start(self):
        """Handle browser start event."""
        self.api.logger.info("Browser started")
    
    def on_browser_exit(self):
        """Handle browser exit event."""
        self.api.logger.info("Browser exiting")
