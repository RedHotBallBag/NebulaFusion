#!/usr/bin/env python3
# NebulaFusion Browser - My Toolbar Button Plugin

from src.plugins.plugin_base import PluginBase


class Plugin(PluginBase):
    """
    My Toolbar Button Plugin for NebulaFusion browser.
    Adds a button to the toolbar that displays a message when clicked.
    """

    def __init__(self, api):
        """Initialize the plugin."""
        super().__init__(api)

    def activate(self):
        """Activate the plugin."""
        return True

    def deactivate(self):
        """Deactivate the plugin."""
        return True

    def onToolbarCreated(self):
        """Called when the browser's toolbar is created."""
        try:
            # Add a button to the toolbar
            self.api.ui.add_toolbar_button(
                button_id="my_button",  # It's good practice to add a unique ID
                text="My Button",
                tooltip="Click me!",
                callback=self.on_button_clicked,
            )

            self.api.logger.info("My Toolbar Button added.")
        except Exception as e:
            self.api.logger.error(f"Error adding toolbar button: {e}")

    def on_button_clicked(self):
        """Called when the button is clicked."""
        self.api.ui.show_message("My Button", "Hello from my toolbar button plugin!")
