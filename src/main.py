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
    # Define the log directory and file path, consistent with Application class
    log_dir = os.path.expanduser("~/.nebulafusion/logs")
    # Create the log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "nebulafusion.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path),  # Use the full path
        ],
    )


def global_exception_hook(exctype, value, tb):
    """Global exception handler to log uncaught exceptions and show a dialog."""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logging.critical(f"Uncaught exception:\n{error_msg}")
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
