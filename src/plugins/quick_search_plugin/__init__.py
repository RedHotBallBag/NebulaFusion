#!/usr/bin/env python3
# NebulaFusion Browser - Quick Search Plugin

from src.plugins.plugin_base import PluginBase


class Plugin(PluginBase):
    """
    Quick Search Plugin for NebulaFusion browser.
    Adds a toolbar button that opens a quick search dialog and navigates to the result.
    """

    def __init__(self, api):
        """Initialize the plugin."""
        super().__init__(api)
        self.search_action = None

    def activate(self):
        return True

    def deactivate(self):
        return True

    def onBrowserStart(self):
        try:
            self.api.ui.add_toolbar_button(
                text="Quick Search",
                tooltip="Search the web",
                callback=self.on_quick_search_clicked,
            )
            self.api.logger.info("Quick Search toolbar button added on browser start.")
        except Exception as e:
            self.api.logger.error(f"Error adding Quick Search toolbar button: {e}")

    def on_quick_search_clicked(self):
        from PyQt6.QtWidgets import QInputDialog

        query, ok = QInputDialog.getText(None, "Quick Search", "Enter search query:")
        if ok and query:
            search_url = self.api.app_controller.settings_manager.get_setting(
                "general.search_engine", "https://www.google.com/search?q="
            )
            url = f"{search_url}{query}"
            self.api.tabs.new_tab(url)
            self.api.ui.show_message("Quick Search", f"Searching: {query}")
