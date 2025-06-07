#!/usr/bin/env python3
# NebulaFusion Browser - Download Manager

import os
import sys
import json
import sqlite3
import time
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

class DownloadManager(QObject):
    """
    Manager for browser downloads.
    Handles downloading, tracking, and managing file downloads.
    """
    
    # Signals
    download_started = pyqtSignal(str, str)  # download_id, url
    download_finished = pyqtSignal(str, str)  # download_id, path
    download_failed = pyqtSignal(str, str)  # download_id, error
    download_progress = pyqtSignal(str, int, int)  # download_id, received, total
    download_canceled = pyqtSignal(str)  # download_id
    
    def __init__(self, app_controller):
        """Initialize the download manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Database connection
        self.db_conn = None
        
        # Active downloads
        self.active_downloads = {}
        
        # Initialize downloads
        self.initialized = False
    
    def initialize(self):
        """Initialize the download manager."""
        self.app_controller.logger.info("Initializing download manager...")
        
        # Create downloads directory
        downloads_dir = os.path.expanduser("~/.nebulafusion/downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Connect to database
        db_path = os.path.join(downloads_dir, "downloads.db")
        self.db_conn = sqlite3.connect(db_path)
        
        # Create tables
        self._create_tables()
        
        # Update state
        self.initialized = True
        
        self.app_controller.logger.info("Download manager initialized.")
        
        return True
    
    def cleanup(self):
        """Clean up the download manager."""
        self.app_controller.logger.info("Cleaning up download manager...")
        
        # Cancel active downloads
        for download_id in list(self.active_downloads.keys()):
            self.cancel_download(download_id)
        
        # Close database connection
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None
        
        # Update state
        self.initialized = False
        
        self.app_controller.logger.info("Download manager cleaned up.")
        
        return True
    
    def _create_tables(self):
        """Create database tables."""
        # Create cursor
        cursor = self.db_conn.cursor()
        
        # Create downloads table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads (
            id TEXT PRIMARY KEY,
            url TEXT,
            path TEXT,
            filename TEXT,
            mime_type TEXT,
            size INTEGER,
            received INTEGER,
            state TEXT,
            start_time INTEGER,
            end_time INTEGER,
            error TEXT
        )
        """)
        
        # Commit changes
        self.db_conn.commit()
    
    def handle_download(self, download):
        """Handle a download request."""
        try:
            # Generate download ID
            download_id = str(int(time.time() * 1000))
            
            # Get download information
            url = download.url().toString()
            suggested_filename = download.suggestedFileName()
            
            # Get download directory
            download_dir = self.app_controller.settings_manager.get_setting("general.download_directory")
            if not download_dir:
                download_dir = os.path.expanduser("~/Downloads")
            
            # Create download directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Set download path
            download_path = os.path.join(download_dir, suggested_filename)
            
            # Check if file exists
            if os.path.exists(download_path):
                # Find a unique filename
                base_name, ext = os.path.splitext(suggested_filename)
                i = 1
                while os.path.exists(download_path):
                    new_filename = f"{base_name} ({i}){ext}"
                    download_path = os.path.join(download_dir, new_filename)
                    i += 1
            
            # Set download path
            download.setDownloadDirectory(download_dir)
            download.setDownloadFileName(os.path.basename(download_path))
            
            # Connect signals
            download.isFinishedChanged.connect(lambda: self._on_download_finished(download_id, download))
            download.receivedBytesChanged.connect(lambda: self._on_download_progress(download_id, download))
            download.stateChanged.connect(lambda: self._on_download_state_changed(download_id, download))
            
            # Accept download
            download.accept()
            
            # Store download
            self.active_downloads[download_id] = download
            
            # Add to database
            self._add_download_to_db(
                download_id,
                url,
                download_path,
                os.path.basename(download_path),
                "",  # MIME type
                0,  # Size
                0,  # Received
                "in_progress",
                int(time.time()),
                0,  # End time
                ""  # Error
            )
            
            # Emit signal
            self.download_started.emit(download_id, url)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadStarted", download_id, url, download_path)
            
            self.app_controller.logger.info(f"Download started: {url} to {download_path}")
            
            return download_id
        
        except Exception as e:
            self.app_controller.logger.error(f"Error handling download: {e}")
            return None
    
    def _add_download_to_db(self, download_id, url, path, filename, mime_type, size, received, state, start_time, end_time, error):
        """Add a download to the database."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Add download
            cursor.execute("""
            INSERT OR REPLACE INTO downloads
            (id, url, path, filename, mime_type, size, received, state, start_time, end_time, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (download_id, url, path, filename, mime_type, size, received, state, start_time, end_time, error))
            
            # Commit changes
            self.db_conn.commit()
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error adding download to database: {e}")
            return False
    
    def _update_download_in_db(self, download_id, **kwargs):
        """Update a download in the database."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Build update query
            query = "UPDATE downloads SET "
            params = []
            
            for key, value in kwargs.items():
                query += f"{key} = ?, "
                params.append(value)
            
            # Remove trailing comma and space
            query = query[:-2]
            
            # Add where clause
            query += " WHERE id = ?"
            params.append(download_id)
            
            # Update download
            cursor.execute(query, params)
            
            # Commit changes
            self.db_conn.commit()
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error updating download in database: {e}")
            return False
    
    def _on_download_finished(self, download_id, download):
        """Handle download finished event."""
        try:
            # Check if download is finished
            if not download.isFinished():
                return
            
            # Get download information
            path = download.downloadDirectory() + "/" + download.downloadFileName()
            
            # Update database
            self._update_download_in_db(
                download_id,
                state="completed" if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadCompleted else "canceled",
                end_time=int(time.time()),
                received=download.receivedBytes(),
                size=download.totalBytes()
            )
            
            # Remove from active downloads
            if download_id in self.active_downloads:
                del self.active_downloads[download_id]
            
            # Emit signal
            self.download_finished.emit(download_id, path)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadFinished", download_id, path)
            
            self.app_controller.logger.info(f"Download finished: {path}")
        
        except Exception as e:
            self.app_controller.logger.error(f"Error handling download finished: {e}")
    
    def _on_download_progress(self, download_id, download):
        """Handle download progress event."""
        try:
            # Get download information
            received = download.receivedBytes()
            total = download.totalBytes()
            
            # Update database
            self._update_download_in_db(
                download_id,
                received=received,
                size=total
            )
            
            # Emit signal
            self.download_progress.emit(download_id, received, total)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadProgress", download_id, received, total)
        
        except Exception as e:
            self.app_controller.logger.error(f"Error handling download progress: {e}")
    
    def _on_download_state_changed(self, download_id, download):
        """Handle download state changed event."""
        try:
            # Get download state
            state = download.state()
            
            # Handle state
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
                # Update database
                self._update_download_in_db(
                    download_id,
                    state="canceled",
                    end_time=int(time.time())
                )
                
                # Remove from active downloads
                if download_id in self.active_downloads:
                    del self.active_downloads[download_id]
                
                # Emit signal
                self.download_canceled.emit(download_id)
                
                # Trigger hook
                self.app_controller.hook_registry.trigger_hook("onDownloadCanceled", download_id)
                
                self.app_controller.logger.info(f"Download canceled: {download_id}")
            
            elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
                # Get error
                error = "Download interrupted"
                
                # Update database
                self._update_download_in_db(
                    download_id,
                    state="failed",
                    end_time=int(time.time()),
                    error=error
                )
                
                # Remove from active downloads
                if download_id in self.active_downloads:
                    del self.active_downloads[download_id]
                
                # Emit signal
                self.download_failed.emit(download_id, error)
                
                # Trigger hook
                self.app_controller.hook_registry.trigger_hook("onDownloadFailed", download_id, error)
                
                self.app_controller.logger.info(f"Download failed: {download_id} - {error}")
        
        except Exception as e:
            self.app_controller.logger.error(f"Error handling download state changed: {e}")
    
    def cancel_download(self, download_id):
        """Cancel a download."""
        try:
            # Check if download exists
            if download_id not in self.active_downloads:
                self.app_controller.logger.warning(f"Download not found: {download_id}")
                return False
            
            # Get download
            download = self.active_downloads[download_id]
            
            # Cancel download
            download.cancel()
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error canceling download: {e}")
            return False
    
    def pause_download(self, download_id):
        """Pause a download."""
        try:
            # Check if download exists
            if download_id not in self.active_downloads:
                self.app_controller.logger.warning(f"Download not found: {download_id}")
                return False
            
            # Get download
            download = self.active_downloads[download_id]
            
            # Pause download
            download.pause()
            
            # Update database
            self._update_download_in_db(
                download_id,
                state="paused"
            )
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadPaused", download_id)
            
            self.app_controller.logger.info(f"Download paused: {download_id}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error pausing download: {e}")
            return False
    
    def resume_download(self, download_id):
        """Resume a download."""
        try:
            # Check if download exists
            if download_id not in self.active_downloads:
                self.app_controller.logger.warning(f"Download not found: {download_id}")
                return False
            
            # Get download
            download = self.active_downloads[download_id]
            
            # Resume download
            download.resume()
            
            # Update database
            self._update_download_in_db(
                download_id,
                state="in_progress"
            )
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadResumed", download_id)
            
            self.app_controller.logger.info(f"Download resumed: {download_id}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error resuming download: {e}")
            return False
    
    def get_download(self, download_id):
        """Get a download."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Get download
            cursor.execute("""
            SELECT id, url, path, filename, mime_type, size, received, state, start_time, end_time, error
            FROM downloads
            WHERE id = ?
            """, (download_id,))
            
            # Get result
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Convert to dictionary
            download = {
                "id": result[0],
                "url": result[1],
                "path": result[2],
                "filename": result[3],
                "mime_type": result[4],
                "size": result[5],
                "received": result[6],
                "state": result[7],
                "start_time": result[8],
                "end_time": result[9],
                "error": result[10]
            }
            
            return download
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting download: {e}")
            return None
    
    def get_downloads(self, limit=100, offset=0, state=None):
        """Get downloads."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Build query
            query = """
            SELECT id, url, path, filename, mime_type, size, received, state, start_time, end_time, error
            FROM downloads
            """
            
            params = []
            
            if state:
                query += "WHERE state = ? "
                params.append(state)
            
            query += "ORDER BY start_time DESC "
            query += "LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Get downloads
            cursor.execute(query, params)
            
            # Convert to list of dictionaries
            downloads = []
            for result in cursor.fetchall():
                download = {
                    "id": result[0],
                    "url": result[1],
                    "path": result[2],
                    "filename": result[3],
                    "mime_type": result[4],
                    "size": result[5],
                    "received": result[6],
                    "state": result[7],
                    "start_time": result[8],
                    "end_time": result[9],
                    "error": result[10]
                }
                downloads.append(download)
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting downloads: {e}")
            return []
    
    def clear_downloads(self, state=None):
        """Clear downloads from the database."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Build query
            query = "DELETE FROM downloads "
            
            params = []
            
            if state:
                query += "WHERE state = ?"
                params.append(state)
            
            # Clear downloads
            cursor.execute(query, params)
            
            # Commit changes
            self.db_conn.commit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadsCleared", state)
            
            self.app_controller.logger.info(f"Downloads cleared: {state or 'all'}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error clearing downloads: {e}")
            return False
    
    def remove_download(self, download_id):
        """Remove a download from the database."""
        try:
            # Create cursor
            cursor = self.db_conn.cursor()
            
            # Remove download
            cursor.execute("""
            DELETE FROM downloads
            WHERE id = ?
            """, (download_id,))
            
            # Commit changes
            self.db_conn.commit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onDownloadRemoved", download_id)
            
            self.app_controller.logger.info(f"Download removed: {download_id}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error removing download: {e}")
            return False
    
    def get_active_downloads(self):
        """Get active downloads."""
        try:
            # Get downloads
            downloads = self.get_downloads(state="in_progress")
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting active downloads: {e}")
            return []
    
    def get_completed_downloads(self):
        """Get completed downloads."""
        try:
            # Get downloads
            downloads = self.get_downloads(state="completed")
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting completed downloads: {e}")
            return []
    
    def get_failed_downloads(self):
        """Get failed downloads."""
        try:
            # Get downloads
            downloads = self.get_downloads(state="failed")
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting failed downloads: {e}")
            return []
    
    def get_canceled_downloads(self):
        """Get canceled downloads."""
        try:
            # Get downloads
            downloads = self.get_downloads(state="canceled")
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting canceled downloads: {e}")
            return []
    
    def get_paused_downloads(self):
        """Get paused downloads."""
        try:
            # Get downloads
            downloads = self.get_downloads(state="paused")
            
            return downloads
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting paused downloads: {e}")
            return []
