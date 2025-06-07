#!/usr/bin/env python3
# NebulaFusion Browser - Main Entry Point

import os
import sys
import logging
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QUrl

# Add parent directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import browser modules
from src.core.application import Application


def setup_logging():
    """Set up logging configuration."""
    # This helper previously configured the root logger which caused duplicate
    # messages when the Application class added its own handlers. It now simply
    # ensures the log directory exists so Application can handle configuration
    # itself.
    log_dir = os.path.expanduser("~/.nebulafusion/logs")
    os.makedirs(log_dir, exist_ok=True)


def global_exception_hook(exctype, value, tb):
    """Global exception handler to log uncaught exceptions and show a dialog."""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    # Use the application logger if available so the message ends up in the
    # same log file as other entries.
    logger = logging.getLogger("NebulaFusion")
    logger.critical(f"Uncaught exception:\n{error_msg}")
    try:
        # Show a user-friendly error dialog if possible
        QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred. See log for details.\n\n{value}")
    except Exception:
        pass  # In case QApplication is not available
    # Call the default excepthook
    sys.__excepthook__(exctype, value, tb)


def main():
    """Main entry point."""
    # Set up logging
    setup_logging()

    # Set global exception hook
    sys.excepthook = global_exception_hook

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("NebulaFusion")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("NebulaFusion")
    app.setOrganizationDomain("nebulafusion.io")

    # Create application controller
    app_controller = Application()

    # Initialize application
    app_controller.initialize()

    # Show main window
    app_controller.show()

    # Start application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
