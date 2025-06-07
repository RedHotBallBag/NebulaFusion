#!/usr/bin/env python3
# Sample Plugin for NebulaFusion Browser

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPainterPath, QAction
from PyQt6.QtCore import Qt, QPointF, QSize
from src.plugins.plugin_base import PluginBase  # <-- ADD THIS IMPORT
import os
import sys


class Plugin(PluginBase):  # <-- ADD THE INHERITANCE
    """
    Sample plugin that demonstrates adding a button to the toolbar.
    """

    def __init__(self, api):
        """Initialize the plugin."""
        super().__init__(api)  # <-- ADD THIS SUPER CALL FOR ROBUSTNESS
        self.button = None

        # Log initialization
        if hasattr(api, "logger"):
            self.api.logger.info(f"Initializing plugin: {self.plugin_id}")

    def activate(self):
        """Activate the plugin."""
        try:
            # Log activation
            if hasattr(self.api, "logger"):
                self.api.logger.info(f"Activating plugin: {self.plugin_id}")

            # Register hooks
            if hasattr(self.api, "hooks"):
                self.api.hooks.register_hook(
                    "onToolbarCreated", self.plugin_id, self.on_toolbar_created
                )

            # Try to add the button immediately if toolbar exists
            main_window = getattr(self.api.app_controller, "main_window", None)
            if main_window and hasattr(main_window, "toolbar"):
                self.add_toolbar_button()

            if hasattr(self.api, "logger"):
                self.api.logger.info(f"Plugin activated: {self.plugin_id}")

            return True

        except Exception as e:
            if hasattr(self.api, "logger"):
                self.api.logger.error(
                    f"Error activating plugin {self.plugin_id}: {str(e)}"
                )
            return False

    def deactivate(self):
        """Deactivate the plugin."""
        try:
            # Remove the button if it exists
            if self.button:
                main_window = getattr(self.api.app_controller, "main_window", None)
                if main_window and hasattr(main_window, "toolbar"):
                    main_window.toolbar.removeAction(self.button)
                    self.button = None

            # Unregister hooks
            if hasattr(self.api, "hooks"):
                self.api.hooks.unregister_all_hooks(self.plugin_id)

            if hasattr(self.api, "logger"):
                self.api.logger.info(f"Plugin deactivated: {self.plugin_id}")

            return True

        except Exception as e:
            if hasattr(self.api, "logger"):
                self.api.logger.error(
                    f"Error deactivating plugin {self.plugin_id}: {str(e)}"
                )
            return False

    def create_star_icon(self):
        """Create a star icon programmatically."""
        try:
            # Create a 24x24 pixmap
            pixmap = QPixmap(24, 24)
            pixmap.fill(Qt.GlobalColor.transparent)

            # Create a painter
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw a star
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 215, 0))  # Gold color

            # Draw a simple star using drawPolygon
            points = [
                QPointF(12, 2),  # Top point
                QPointF(15, 9),  # Right middle outer
                QPointF(22, 9),  # Right middle
                QPointF(16, 14),  # Bottom right outer
                QPointF(19, 21),  # Bottom right
                QPointF(12, 17),  # Bottom point
                QPointF(5, 21),  # Bottom left
                QPointF(8, 14),  # Bottom left outer
                QPointF(2, 9),  # Left middle
                QPointF(9, 9),  # Left middle outer
            ]

            # Draw the star
            painter.drawPolygon(points)
            painter.end()
            return QIcon(pixmap)

        except Exception as e:
            if hasattr(self.api, "logger"):
                self.api.logger.error(f"Error creating icon: {str(e)}")
            return QIcon()

    def on_toolbar_created(self):
        """Handle toolbar created event."""
        if hasattr(self.api, "logger"):
            self.api.logger.info("Toolbar created, adding button...")
        self.add_toolbar_button()

    def add_toolbar_button(self):
        """Add a button to the toolbar."""
        try:
            if self.button is not None:  # Button already added
                return

            # Create a star icon
            star_icon = self.create_star_icon()

            if hasattr(self.api, "logger"):
                self.api.logger.info("Adding toolbar button...")

            # Add the button to the toolbar
            self.button = self.api.ui.add_toolbar_button(
                button_id="sample_button",
                text="Sample",
                icon=star_icon,
                tooltip="Click me! I'm a sample plugin button.",
                callback=self.on_button_clicked,
            )

            if hasattr(self.api, "logger"):
                if self.button:
                    self.api.logger.info("Successfully added toolbar button")
                else:
                    self.api.logger.error("Failed to add toolbar button")

        except Exception as e:
            if hasattr(self.api, "logger"):
                self.api.logger.error(f"Error adding toolbar button: {str(e)}")

    def on_button_clicked(self):
        """Handle button click."""
        try:
            if hasattr(self.api, "ui"):
                self.api.ui.show_message(
                    "Sample Plugin",
                    "Hello from the sample plugin!\n\n"
                    "This button was added by a plugin.",
                )
        except Exception as e:
            if hasattr(self.api, "logger"):
                self.api.logger.error(f"Error in button click handler: {str(e)}")
