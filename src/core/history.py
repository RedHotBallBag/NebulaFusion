#!/usr/bin/env python3
# NebulaFusion Browser - History Manager

import os
import sys
import json
import sqlite3
import time
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

class HistoryManager(QObject):
    """
    Manager for browser history.
    Handles storing, retrieving, and managing browsing history.
    """
    
    # Signals
    history_added = pyqtSignal(str, str)  # url, title
    history_removed = pyqtSignal(str)  # url
    history_cleared = pyqtSignal()
    
    def __init__(self, app_controller):
        """Initialize the history manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Database connection
        self.db_conn = None
        
        # Initialize history
        self.initialized = False
        
        # Private browsing mode
        self.private_mode = False
    
    def initialize(self):
        """Initialize the history manager."""
        self.app_controller.logger.info("Initializing history manager...")
        
        # Create history directory
        history_dir = os.path.expanduser("~/.nebulafusion/history")
        os.makedirs(history_dir, exist_ok=True)
        
        # Connect to database
        db_path = os.path.join(history_dir, "history.db")
        self.db_conn = sqlite3.connect(db_path)
        
        # Create tables
        self._create_tables()
        
        # Update state
        self.initialized = True
        
        self.app_controller.logger.info("History manager initialized.")
        
        return True
    
    def cleanup(self):
        """Clean up the history manager."""
        self.app_controller.logger.info("Cleaning up history manager...")
        
        # Close database connection
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None
        
        # Update state
        self.initialized = False
        
        self.app_controller.logger.info("History manager cleaned up.")
        
        return True
    
    def _create_tables(self):
        """Create database tables."""
        # Create cursor
        cursor = self.db_conn.cursor()
        
        # Create history table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            visit_time INTEGER,
            visit_count INTEGER DEFAULT 1
        )
        """)
        
        # Create index on url
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_url ON history (url)
        """)
        
        # Create index on visit_time
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_visit_time ON history (visit_time)
        """)
        
        # Commit changes
        self.db_conn.commit()
    
    def add_history(self, url, title):
        """Add a history entry."""
        # Skip if in private mode
        if self.private_mode:
            return True
        
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get current time
            current_time = int(time.time())
            
            # Check if URL exists
            cursor.execute("""
            SELECT id, visit_count FROM history WHERE url = ?
            """, (url,))
            
            result = cursor.fetchone()
            
            if result:
                # Update existing entry
                entry_id, visit_count = result
                
                cursor.execute("""
                UPDATE history
                SET title = ?, visit_time = ?, visit_count = ?
                WHERE id = ?
                """, (title, current_time, visit_count + 1, entry_id))
            else:
                # Add new entry
                cursor.execute("""
                INSERT INTO history (url, title, visit_time)
                VALUES (?, ?, ?)
                """, (url, title, current_time))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.history_added.emit(url, title)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onHistoryAdded", url, title)
            
            self.app_controller.logger.info(f"History entry added: {url}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error adding history entry: {e}")
            return False
    
    def remove_history(self, url):
        """Remove a history entry."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Remove entry
            cursor.execute("""
            DELETE FROM history WHERE url = ?
            """, (url,))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.history_removed.emit(url)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onHistoryRemoved", url)
            
            self.app_controller.logger.info(f"History entry removed: {url}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error removing history entry: {e}")
            return False
    
    def clear_history(self):
        """Clear all history."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Clear history
            cursor.execute("""
            DELETE FROM history
            """)
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.history_cleared.emit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onHistoryCleared")
            
            self.app_controller.logger.info("History cleared")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error clearing history: {e}")
            return False
    
    def get_history(self, limit=100, offset=0):
        """Get history entries."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get history
            cursor.execute("""
            SELECT url, title, visit_time, visit_count
            FROM history
            ORDER BY visit_time DESC
            LIMIT ? OFFSET ?
            """, (limit, offset))
            
            # Convert to list of dictionaries
            history = []
            for row in cursor.fetchall():
                url, title, visit_time, visit_count = row
                history.append({
                    "url": url,
                    "title": title,
                    "visit_time": visit_time,
                    "visit_count": visit_count
                })
            
            return history
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting history: {e}")
            return []
    
    def search_history(self, query, limit=100, offset=0):
        """Search history entries."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Search history
            cursor.execute("""
            SELECT url, title, visit_time, visit_count
            FROM history
            WHERE url LIKE ? OR title LIKE ?
            ORDER BY visit_time DESC
            LIMIT ? OFFSET ?
            """, (f"%{query}%", f"%{query}%", limit, offset))
            
            # Convert to list of dictionaries
            history = []
            for row in cursor.fetchall():
                url, title, visit_time, visit_count = row
                history.append({
                    "url": url,
                    "title": title,
                    "visit_time": visit_time,
                    "visit_count": visit_count
                })
            
            return history
        
        except Exception as e:
            self.app_controller.logger.error(f"Error searching history: {e}")
            return []
    
    def get_most_visited(self, limit=10):
        """Get most visited sites."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get most visited sites
            cursor.execute("""
            SELECT url, title, visit_time, visit_count
            FROM history
            ORDER BY visit_count DESC
            LIMIT ?
            """, (limit,))
            
            # Convert to list of dictionaries
            history = []
            for row in cursor.fetchall():
                url, title, visit_time, visit_count = row
                history.append({
                    "url": url,
                    "title": title,
                    "visit_time": visit_time,
                    "visit_count": visit_count
                })
            
            return history
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting most visited sites: {e}")
            return []
    
    def get_recent(self, limit=10):
        """Get recently visited sites."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get recent sites
            cursor.execute("""
            SELECT url, title, visit_time, visit_count
            FROM history
            ORDER BY visit_time DESC
            LIMIT ?
            """, (limit,))
            
            # Convert to list of dictionaries
            history = []
            for row in cursor.fetchall():
                url, title, visit_time, visit_count = row
                history.append({
                    "url": url,
                    "title": title,
                    "visit_time": visit_time,
                    "visit_count": visit_count
                })
            
            return history
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting recent sites: {e}")
            return []
    
    def export_history(self, file_path):
        """Export history to a file."""
        try:
            # Get all history
            history = self.get_history(limit=0)
            
            # Check file extension
            if file_path.endswith(".json"):
                # Export to JSON
                with open(file_path, "w") as f:
                    json.dump(history, f, indent=4)
            
            elif file_path.endswith(".csv"):
                # Export to CSV
                import csv
                
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(["URL", "Title", "Visit Time", "Visit Count"])
                    
                    # Write data
                    for entry in history:
                        writer.writerow([
                            entry["url"],
                            entry["title"],
                            entry["visit_time"],
                            entry["visit_count"]
                        ])
            
            else:
                self.app_controller.logger.error("Unsupported history file format")
                return False
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onHistoryExported")
            
            self.app_controller.logger.info(f"History exported to {file_path}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error exporting history: {e}")
            return False
    
    def import_history(self, file_path):
        """Import history from a file."""
        try:
            # Check file extension
            if file_path.endswith(".json"):
                # Import from JSON
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                # Check if data is valid
                if not isinstance(data, list):
                    self.app_controller.logger.error("Invalid history file format")
                    return False
                
                # Import history
                for entry in data:
                    if "url" in entry and "title" in entry:
                        self.add_history(entry["url"], entry["title"])
            
            elif file_path.endswith(".csv"):
                # Import from CSV
                import csv
                
                with open(file_path, "r", newline="") as f:
                    reader = csv.reader(f)
                    
                    # Skip header
                    next(reader)
                    
                    # Import history
                    for row in reader:
                        if len(row) >= 2:
                            url, title = row[0], row[1]
                            self.add_history(url, title)
            
            else:
                self.app_controller.logger.error("Unsupported history file format")
                return False
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onHistoryImported")
            
            self.app_controller.logger.info(f"History imported from {file_path}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error importing history: {e}")
            return False
    
    def set_private_mode(self, enabled):
        """Set private browsing mode."""
        self.private_mode = enabled
        
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onPrivateModeChanged", enabled)
        
        self.app_controller.logger.info(f"Private browsing mode: {enabled}")
        
        return True
    
    def is_private_mode(self):
        """Check if private browsing mode is enabled."""
        return self.private_mode
