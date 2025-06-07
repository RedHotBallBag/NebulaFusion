#!/usr/bin/env python3
# NebulaFusion Browser - Bookmarks Manager

import os
import sys
import json
import sqlite3
import time
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

class BookmarksManager(QObject):
    """
    Manager for browser bookmarks.
    Handles storing, retrieving, and managing bookmarks.
    """
    
    # Signals
    bookmark_added = pyqtSignal(str, str, str)  # url, title, folder
    bookmark_removed = pyqtSignal(str, str)  # url, folder
    bookmark_updated = pyqtSignal(str, str, str, str)  # old_url, new_url, new_title, new_folder
    folder_added = pyqtSignal(str)  # folder_name
    folder_removed = pyqtSignal(str)  # folder_name
    folder_renamed = pyqtSignal(str, str)  # old_name, new_name
    bookmarks_imported = pyqtSignal()
    bookmarks_exported = pyqtSignal()
    
    def __init__(self, app_controller):
        """Initialize the bookmarks manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Database connection
        self.db_conn = None
        
        # Default folders
        self.default_folders = [
            "Bookmarks Bar",
            "Other Bookmarks",
            "Mobile Bookmarks"
        ]
        
        # Initialize bookmarks
        self.initialized = False
    
    def initialize(self):
        """Initialize the bookmarks manager."""
        self.app_controller.logger.info("Initializing bookmarks manager...")
        
        # Create bookmarks directory
        bookmarks_dir = os.path.expanduser("~/.nebulafusion/bookmarks")
        os.makedirs(bookmarks_dir, exist_ok=True)
        
        # Connect to database
        db_path = os.path.join(bookmarks_dir, "bookmarks.db")
        self.db_conn = sqlite3.connect(db_path)
        
        # Create tables
        self._create_tables()
        
        # Create default folders
        self._create_default_folders()
        
        # Update state
        self.initialized = True
        
        self.app_controller.logger.info("Bookmarks manager initialized.")
        
        return True
    
    def cleanup(self):
        """Clean up the bookmarks manager."""
        self.app_controller.logger.info("Cleaning up bookmarks manager...")
        
        # Close database connection
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None
        
        # Update state
        self.initialized = False
        
        self.app_controller.logger.info("Bookmarks manager cleaned up.")
        
        return True
    
    def _create_tables(self):
        """Create database tables."""
        # Create cursor
        cursor = self.db_conn.cursor()
        
        # Create folders table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at INTEGER,
            updated_at INTEGER
        )
        """)
        
        # Create bookmarks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            folder_id INTEGER,
            created_at INTEGER,
            updated_at INTEGER,
            FOREIGN KEY (folder_id) REFERENCES folders (id),
            UNIQUE (url, folder_id)
        )
        """)
        
        # Commit changes
        self.db_conn.commit()
    
    def _create_default_folders(self):
        """Create default folders."""
        # Create cursor
        cursor = self.db_conn.cursor()
        
        # Get current time
        current_time = int(time.time())
        
        # Create default folders
        for folder_name in self.default_folders:
            cursor.execute("""
            INSERT OR IGNORE INTO folders (name, created_at, updated_at)
            VALUES (?, ?, ?)
            """, (folder_name, current_time, current_time))
        
        # Commit changes
        self.db_conn.commit()
    
    def add_bookmark(self, url, title, folder="Bookmarks Bar"):
        """Add a bookmark."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get current time
            current_time = int(time.time())
            
            # Get folder ID
            cursor.execute("""
            SELECT id FROM folders WHERE name = ?
            """, (folder,))
            
            folder_id = cursor.fetchone()
            
            if not folder_id:
                # Create folder
                self.add_folder(folder)
                
                # Get folder ID
                cursor.execute("""
                SELECT id FROM folders WHERE name = ?
                """, (folder,))
                
                folder_id = cursor.fetchone()
            
            folder_id = folder_id[0]
            
            # Add bookmark
            cursor.execute("""
            INSERT OR REPLACE INTO bookmarks (url, title, folder_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (url, title, folder_id, current_time, current_time))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.bookmark_added.emit(url, title, folder)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkAdded", url, title, folder)
            
            self.app_controller.logger.info(f"Bookmark added: {url} in {folder}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error adding bookmark: {e}")
            return False
    
    def remove_bookmark(self, url, folder=None):
        """Remove a bookmark."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            if folder:
                # Get folder ID
                cursor.execute("""
                SELECT id FROM folders WHERE name = ?
                """, (folder,))
                
                folder_id = cursor.fetchone()
                
                if not folder_id:
                    self.app_controller.logger.warning(f"Folder not found: {folder}")
                    return False
                
                folder_id = folder_id[0]
                
                # Remove bookmark
                cursor.execute("""
                DELETE FROM bookmarks WHERE url = ? AND folder_id = ?
                """, (url, folder_id))
            else:
                # Remove bookmark from all folders
                cursor.execute("""
                DELETE FROM bookmarks WHERE url = ?
                """, (url,))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.bookmark_removed.emit(url, folder or "all")
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkRemoved", url, folder)
            
            self.app_controller.logger.info(f"Bookmark removed: {url} from {folder or 'all'}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error removing bookmark: {e}")
            return False
    
    def update_bookmark(self, url, new_url=None, new_title=None, new_folder=None):
        """Update a bookmark."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get current time
            current_time = int(time.time())
            
            # Get bookmark
            cursor.execute("""
            SELECT b.id, b.title, f.name
            FROM bookmarks b
            JOIN folders f ON b.folder_id = f.id
            WHERE b.url = ?
            """, (url,))
            
            bookmark = cursor.fetchone()
            
            if not bookmark:
                self.app_controller.logger.warning(f"Bookmark not found: {url}")
                return False
            
            bookmark_id, title, folder = bookmark
            
            # Update bookmark
            if new_folder and new_folder != folder:
                # Get new folder ID
                cursor.execute("""
                SELECT id FROM folders WHERE name = ?
                """, (new_folder,))
                
                new_folder_id = cursor.fetchone()
                
                if not new_folder_id:
                    # Create folder
                    self.add_folder(new_folder)
                    
                    # Get folder ID
                    cursor.execute("""
                    SELECT id FROM folders WHERE name = ?
                    """, (new_folder,))
                    
                    new_folder_id = cursor.fetchone()
                
                new_folder_id = new_folder_id[0]
                
                # Update bookmark
                cursor.execute("""
                UPDATE bookmarks
                SET url = ?, title = ?, folder_id = ?, updated_at = ?
                WHERE id = ?
                """, (new_url or url, new_title or title, new_folder_id, current_time, bookmark_id))
            else:
                # Update bookmark
                cursor.execute("""
                UPDATE bookmarks
                SET url = ?, title = ?, updated_at = ?
                WHERE id = ?
                """, (new_url or url, new_title or title, current_time, bookmark_id))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.bookmark_updated.emit(url, new_url or url, new_title or title, new_folder or folder)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkUpdated", url, new_url or url, new_title or title, new_folder or folder)
            
            self.app_controller.logger.info(f"Bookmark updated: {url} to {new_url or url}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error updating bookmark: {e}")
            return False
    
    def add_folder(self, folder_name):
        """Add a bookmark folder."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get current time
            current_time = int(time.time())
            
            # Add folder
            cursor.execute("""
            INSERT OR IGNORE INTO folders (name, created_at, updated_at)
            VALUES (?, ?, ?)
            """, (folder_name, current_time, current_time))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.folder_added.emit(folder_name)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkFolderAdded", folder_name)
            
            self.app_controller.logger.info(f"Bookmark folder added: {folder_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error adding bookmark folder: {e}")
            return False
    
    def remove_folder(self, folder_name):
        """Remove a bookmark folder."""
        try:
            # Check if folder is a default folder
            if folder_name in self.default_folders:
                self.app_controller.logger.warning(f"Cannot remove default folder: {folder_name}")
                return False
            
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get folder ID
            cursor.execute("""
            SELECT id FROM folders WHERE name = ?
            """, (folder_name,))
            
            folder_id = cursor.fetchone()
            
            if not folder_id:
                self.app_controller.logger.warning(f"Folder not found: {folder_name}")
                return False
            
            folder_id = folder_id[0]
            
            # Remove bookmarks in folder
            cursor.execute("""
            DELETE FROM bookmarks WHERE folder_id = ?
            """, (folder_id,))
            
            # Remove folder
            cursor.execute("""
            DELETE FROM folders WHERE id = ?
            """, (folder_id,))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.folder_removed.emit(folder_name)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkFolderRemoved", folder_name)
            
            self.app_controller.logger.info(f"Bookmark folder removed: {folder_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error removing bookmark folder: {e}")
            return False
    
    def rename_folder(self, old_name, new_name):
        """Rename a bookmark folder."""
        try:
            # Check if folder is a default folder
            if old_name in self.default_folders:
                self.app_controller.logger.warning(f"Cannot rename default folder: {old_name}")
                return False
            
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get current time
            current_time = int(time.time())
            
            # Rename folder
            cursor.execute("""
            UPDATE folders
            SET name = ?, updated_at = ?
            WHERE name = ?
            """, (new_name, current_time, old_name))
            
            # Commit changes
            self.db_conn.commit()
            
            # Emit signal
            self.folder_renamed.emit(old_name, new_name)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarkFolderRenamed", old_name, new_name)
            
            self.app_controller.logger.info(f"Bookmark folder renamed: {old_name} to {new_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error renaming bookmark folder: {e}")
            return False
    
    def get_bookmarks(self, folder=None):
        """Get bookmarks."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            if folder:
                # Get folder ID
                cursor.execute("""
                SELECT id FROM folders WHERE name = ?
                """, (folder,))
                
                folder_id = cursor.fetchone()
                
                if not folder_id:
                    self.app_controller.logger.warning(f"Folder not found: {folder}")
                    return []
                
                folder_id = folder_id[0]
                
                # Get bookmarks
                cursor.execute("""
                SELECT b.url, b.title, f.name, b.created_at, b.updated_at
                FROM bookmarks b
                JOIN folders f ON b.folder_id = f.id
                WHERE b.folder_id = ?
                ORDER BY b.title
                """, (folder_id,))
            else:
                # Get all bookmarks
                cursor.execute("""
                SELECT b.url, b.title, f.name, b.created_at, b.updated_at
                FROM bookmarks b
                JOIN folders f ON b.folder_id = f.id
                ORDER BY f.name, b.title
                """)
            
            # Convert to list of dictionaries
            bookmarks = []
            for row in cursor.fetchall():
                url, title, folder_name, created_at, updated_at = row
                bookmarks.append({
                    "url": url,
                    "title": title,
                    "folder": folder_name,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            return bookmarks
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting bookmarks: {e}")
            return []
    
    def get_folders(self):
        """Get bookmark folders."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get folders
            cursor.execute("""
            SELECT name FROM folders ORDER BY name
            """)
            
            # Convert to list
            folders = [row[0] for row in cursor.fetchall()]
            
            return folders
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting bookmark folders: {e}")
            return []
    
    def search_bookmarks(self, query):
        """Search bookmarks."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Search bookmarks
            cursor.execute("""
            SELECT b.url, b.title, f.name, b.created_at, b.updated_at
            FROM bookmarks b
            JOIN folders f ON b.folder_id = f.id
            WHERE b.url LIKE ? OR b.title LIKE ?
            ORDER BY f.name, b.title
            """, (f"%{query}%", f"%{query}%"))
            
            # Convert to list of dictionaries
            bookmarks = []
            for row in cursor.fetchall():
                url, title, folder_name, created_at, updated_at = row
                bookmarks.append({
                    "url": url,
                    "title": title,
                    "folder": folder_name,
                    "created_at": created_at,
                    "updated_at": updated_at
                })
            
            return bookmarks
        
        except Exception as e:
            self.app_controller.logger.error(f"Error searching bookmarks: {e}")
            return []
    
    def import_bookmarks(self, file_path):
        """Import bookmarks from a file."""
        try:
            # Check file extension
            if file_path.endswith(".json"):
                # Import from JSON
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                # Check if data is valid
                if not isinstance(data, list):
                    self.app_controller.logger.error("Invalid bookmarks file format")
                    return False
                
                # Import bookmarks
                for bookmark in data:
                    if "url" in bookmark and "title" in bookmark:
                        folder = bookmark.get("folder", "Imported Bookmarks")
                        self.add_bookmark(bookmark["url"], bookmark["title"], folder)
            
            elif file_path.endswith(".html") or file_path.endswith(".htm"):
                # Import from HTML
                with open(file_path, "r") as f:
                    content = f.read()
                
                # Parse HTML
                import re
                
                # Find all links
                links = re.findall(r'<A HREF="([^"]+)"[^>]*>([^<]+)</A>', content)
                
                # Import bookmarks
                for url, title in links:
                    self.add_bookmark(url, title, "Imported Bookmarks")
            
            else:
                self.app_controller.logger.error("Unsupported bookmarks file format")
                return False
            
            # Emit signal
            self.bookmarks_imported.emit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarksImported")
            
            self.app_controller.logger.info(f"Bookmarks imported from {file_path}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error importing bookmarks: {e}")
            return False
    
    def export_bookmarks(self, file_path):
        """Export bookmarks to a file."""
        try:
            # Get all bookmarks
            bookmarks = self.get_bookmarks()
            
            # Check file extension
            if file_path.endswith(".json"):
                # Export to JSON
                with open(file_path, "w") as f:
                    json.dump(bookmarks, f, indent=4)
            
            elif file_path.endswith(".html") or file_path.endswith(".htm"):
                # Export to HTML
                with open(file_path, "w") as f:
                    f.write('<!DOCTYPE NETSCAPE-Bookmark-file-1>\n')
                    f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
                    f.write('<TITLE>Bookmarks</TITLE>\n')
                    f.write('<H1>Bookmarks</H1>\n')
                    f.write('<DL><p>\n')
                    
                    # Group bookmarks by folder
                    folders = {}
                    for bookmark in bookmarks:
                        folder = bookmark["folder"]
                        if folder not in folders:
                            folders[folder] = []
                        folders[folder].append(bookmark)
                    
                    # Write folders
                    for folder, folder_bookmarks in folders.items():
                        f.write(f'    <DT><H3>{folder}</H3>\n')
                        f.write('    <DL><p>\n')
                        
                        # Write bookmarks
                        for bookmark in folder_bookmarks:
                            f.write(f'        <DT><A HREF="{bookmark["url"]}">{bookmark["title"]}</A>\n')
                        
                        f.write('    </DL><p>\n')
                    
                    f.write('</DL><p>\n')
            
            else:
                self.app_controller.logger.error("Unsupported bookmarks file format")
                return False
            
            # Emit signal
            self.bookmarks_exported.emit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onBookmarksExported")
            
            self.app_controller.logger.info(f"Bookmarks exported to {file_path}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error exporting bookmarks: {e}")
            return False
    
    def is_bookmarked(self, url, folder=None):
        """Check if a URL is bookmarked."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            if folder:
                # Get folder ID
                cursor.execute("""
                SELECT id FROM folders WHERE name = ?
                """, (folder,))
                
                folder_id = cursor.fetchone()
                
                if not folder_id:
                    return False
                
                folder_id = folder_id[0]
                
                # Check if URL is bookmarked
                cursor.execute("""
                SELECT COUNT(*) FROM bookmarks WHERE url = ? AND folder_id = ?
                """, (url, folder_id))
            else:
                # Check if URL is bookmarked in any folder
                cursor.execute("""
                SELECT COUNT(*) FROM bookmarks WHERE url = ?
                """, (url,))
            
            # Get result
            count = cursor.fetchone()[0]
            
            return count > 0
        
        except Exception as e:
            self.app_controller.logger.error(f"Error checking if URL is bookmarked: {e}")
            return False
