#!/usr/bin/env python3
# NebulaFusion Browser - Logger Utility

import os
import sys
import logging
import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class Logger(QObject):
    """
    Logger utility for NebulaFusion browser.
    Provides logging functionality with different log levels and outputs.
    """
    
    # Signals
    log_added = pyqtSignal(str, str, str)  # level, module, message
    
    def __init__(self, module_name):
        """Initialize the logger."""
        super().__init__()
        self.module_name = module_name
        
        # Create logger
        self.logger = logging.getLogger(f"nebulafusion.{module_name}")
        
        # Set default level
        self.logger.setLevel(logging.INFO)
        
        # Check if handlers already exist
        if not self.logger.handlers:
            # Create log directory if it doesn't exist
            log_dir = os.path.expanduser("~/.nebulafusion/logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log file path
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"nebulafusion_{today}.log")
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Create console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def set_level(self, level):
        """Set the logger level."""
        if level == "debug":
            self.logger.setLevel(logging.DEBUG)
        elif level == "info":
            self.logger.setLevel(logging.INFO)
        elif level == "warning":
            self.logger.setLevel(logging.WARNING)
        elif level == "error":
            self.logger.setLevel(logging.ERROR)
        elif level == "critical":
            self.logger.setLevel(logging.CRITICAL)
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
        self.log_added.emit("debug", self.module_name, message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
        self.log_added.emit("info", self.module_name, message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
        self.log_added.emit("warning", self.module_name, message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
        self.log_added.emit("error", self.module_name, message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
        self.log_added.emit("critical", self.module_name, message)
    
    def exception(self, message):
        """Log an exception message."""
        self.logger.exception(message)
        self.log_added.emit("exception", self.module_name, message)
    
    @staticmethod
    def get_all_logs(limit=100):
        """Get all logs from the log file."""
        log_dir = os.path.expanduser("~/.nebulafusion/logs")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"nebulafusion_{today}.log")
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        # Return last 'limit' lines
        return lines[-limit:]
    
    @staticmethod
    def clear_logs():
        """Clear all logs."""
        log_dir = os.path.expanduser("~/.nebulafusion/logs")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"nebulafusion_{today}.log")
        
        if os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write("")
