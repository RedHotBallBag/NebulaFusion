#!/usr/bin/env python3
# NebulaFusion Browser - Security Manager

import os
import json
import time
import hashlib
import sqlite3
from PyQt6.QtCore import QObject, pyqtSignal


class SecurityManager(QObject):
    """
    Manages browser security features.
    """

    # Signals
    security_alert = pyqtSignal(str, str, int)

    def __init__(self, app_controller):
        """Initialize the security manager."""
        super().__init__()
        self.app_controller = app_controller

        # Set security database path
        self.security_db = os.path.expanduser("~/.nebulafusion/security.db")

        # Initialize database connection
        self.conn = None
        self.cursor = None

        # Security settings
        self.security_settings = {
            "block_malicious_sites": True,
            "warn_on_insecure_forms": True,
            "enable_phishing_protection": True,
            "enable_xss_protection": True,
            "enable_content_verification": True,
            "plugin_sandbox_enabled": True,
            "plugin_resource_limits": {
                "cpu_percent": 10,
                "memory_mb": 100,
                "network_requests_per_minute": 60,
                "file_access_paths": ["~/.nebulafusion/plugins"],
            },
        }

        # Malicious site indicators
        self.malicious_indicators = [
            "phishing",
            "malware",
            "scam",
            "virus",
            "trojan",
            "exploit",
        ]

    def initialize(self):
        """Initialize the security manager."""
        # Create security directory if it doesn't exist
        os.makedirs(os.path.dirname(self.security_db), exist_ok=True)

        # Connect to database
        self.conn = sqlite3.connect(self.security_db)
        self.cursor = self.conn.cursor()

        # Create tables if they don't exist
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                url TEXT,
                description TEXT NOT NULL,
                severity INTEGER NOT NULL,
                timestamp REAL NOT NULL
            )
        """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS blocked_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                reason TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        """
        )

        # Create indexes
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events (event_type)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events (timestamp)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_blocked_sites_url ON blocked_sites (url)"
        )

        # Commit changes
        self.conn.commit()

        # Load security settings
        self.load_security_settings()

    def load_security_settings(self):
        """Load security settings from settings manager."""
        # Get security settings from settings manager
        for key in self.security_settings.keys():
            if key != "plugin_resource_limits":
                value = self.app_controller.settings_manager.get_setting(
                    f"security_{key}", self.security_settings[key]
                )
                self.security_settings[key] = value

        # Get plugin resource limits
        for key in self.security_settings["plugin_resource_limits"].keys():
            value = self.app_controller.settings_manager.get_setting(
                f"security_plugin_{key}",
                self.security_settings["plugin_resource_limits"][key],
            )
            self.security_settings["plugin_resource_limits"][key] = value

    def check_url_security(self, url):
        """Check if a URL is secure."""
        # Check if URL is HTTPS
        is_https = url.startswith("https://")

        # Check if URL is in blocked sites
        is_blocked = self.is_url_blocked(url)

        # Check for malicious indicators
        has_malicious_indicators = any(
            indicator in url.lower() for indicator in self.malicious_indicators
        )

        # Return security status
        return {
            "is_secure": is_https and not is_blocked and not has_malicious_indicators,
            "is_https": is_https,
            "is_blocked": is_blocked,
            "has_malicious_indicators": has_malicious_indicators,
        }

    def is_url_blocked(self, url):
        """Check if a URL is blocked."""
        try:
            # Check database
            self.cursor.execute("SELECT id FROM blocked_sites WHERE url = ?", (url,))
            result = self.cursor.fetchone()

            return result is not None

        except Exception as e:
            print(f"Error checking blocked URL: {e}")
            return False

    def block_url(self, url, reason):
        """Block a URL."""
        try:
            # Check if URL is already blocked
            if self.is_url_blocked(url):
                return True

            # Add to blocked sites
            self.cursor.execute(
                "INSERT INTO blocked_sites (url, reason, timestamp) VALUES (?, ?, ?)",
                (url, reason, time.time()),
            )

            # Commit changes
            self.conn.commit()

            # Log security event
            self.log_security_event("url_blocked", url, f"URL blocked: {reason}", 2)

            return True

        except Exception as e:
            print(f"Error blocking URL: {e}")
            # Rollback changes
            self.conn.rollback()
            return False

    def unblock_url(self, url):
        """Unblock a URL."""
        try:
            # Remove from blocked sites
            self.cursor.execute("DELETE FROM blocked_sites WHERE url = ?", (url,))

            # Commit changes
            self.conn.commit()

            # Log security event
            self.log_security_event("url_unblocked", url, "URL unblocked", 1)

            return True

        except Exception as e:
            print(f"Error unblocking URL: {e}")
            # Rollback changes
            self.conn.rollback()
            return False

    def get_blocked_urls(self):
        """Get blocked URLs."""
        try:
            # Get blocked sites
            self.cursor.execute(
                "SELECT url, reason, timestamp FROM blocked_sites ORDER BY timestamp DESC"
            )

            # Return results
            return [
                {"url": row[0], "reason": row[1], "timestamp": row[2]}
                for row in self.cursor.fetchall()
            ]

        except Exception as e:
            print(f"Error getting blocked URLs: {e}")
            return []

    def log_security_event(self, event_type, url, description, severity):
        """Log a security event."""
        try:
            # Add to security events
            self.cursor.execute(
                """
                INSERT INTO security_events 
                (event_type, url, description, severity, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (event_type, url, description, severity, time.time()),
            )

            # Commit changes
            self.conn.commit()

            # Emit signal for high severity events
            if severity >= 2:
                self.security_alert.emit(event_type, description, severity)

            return True

        except Exception as e:
            print(f"Error logging security event: {e}")
            # Rollback changes
            self.conn.rollback()
            return False

    def get_security_events(self, event_type=None, severity=None, limit=100, offset=0):
        """Get security events."""
        try:
            query = "SELECT event_type, url, description, severity, timestamp FROM security_events"
            params = []

            # Add filters
            if event_type or severity is not None:
                query += " WHERE"

                if event_type:
                    query += " event_type = ?"
                    params.append(event_type)

                if severity is not None:
                    if event_type:
                        query += " AND"
                    query += " severity >= ?"
                    params.append(severity)

            # Add order and limit
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            # Execute query
            self.cursor.execute(query, params)

            # Return results
            return [
                {
                    "event_type": row[0],
                    "url": row[1],
                    "description": row[2],
                    "severity": row[3],
                    "timestamp": row[4],
                }
                for row in self.cursor.fetchall()
            ]

        except Exception as e:
            print(f"Error getting security events: {e}")
            return []

    def clear_security_events(self):
        """Clear security events."""
        try:
            # Delete all security events
            self.cursor.execute("DELETE FROM security_events")

            # Commit changes
            self.conn.commit()

            return True

        except Exception as e:
            print(f"Error clearing security events: {e}")
            # Rollback changes
            self.conn.rollback()
            return False

    def verify_plugin_integrity(self, plugin_path):
        """Verify plugin integrity."""
        try:
            # Check if plugin exists
            if not os.path.exists(plugin_path):
                return False, "Plugin does not exist"

            # Check if plugin is a directory
            if not os.path.isdir(plugin_path):
                return False, "Plugin is not a directory"

            # Check if plugin has required files
            required_files = ["__init__.py", "manifest.json"]
            for file in required_files:
                if not os.path.exists(os.path.join(plugin_path, file)):
                    return False, f"Plugin is missing required file: {file}"

            # Check manifest.json
            try:
                with open(os.path.join(plugin_path, "manifest.json"), "r") as f:
                    manifest = json.load(f)

                # Check required fields
                required_fields = ["name", "version", "author", "description"]
                for field in required_fields:
                    if field not in manifest:
                        return (
                            False,
                            f"Plugin manifest is missing required field: {field}",
                        )

            except Exception as e:
                return False, f"Error parsing plugin manifest: {e}"

            # Calculate plugin hash
            plugin_hash = self.calculate_plugin_hash(plugin_path)

            # TODO: Verify plugin hash against trusted repository

            return True, "Plugin integrity verified"

        except Exception as e:
            return False, f"Error verifying plugin integrity: {e}"

    def calculate_plugin_hash(self, plugin_path):
        """Calculate plugin hash."""
        try:
            # Initialize hasher
            hasher = hashlib.sha256()

            # Get all files in plugin directory
            for root, dirs, files in os.walk(plugin_path):
                for file in sorted(files):
                    file_path = os.path.join(root, file)

                    # Skip __pycache__ and other non-source files
                    if "__pycache__" in file_path or file.endswith(".pyc"):
                        continue

                    # Read file and update hash
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())

            # Return hash
            return hasher.hexdigest()

        except Exception as e:
            print(f"Error calculating plugin hash: {e}")
            return None

    def check_plugin_permissions(self, plugin_manifest, requested_permissions):
        """Check plugin permissions."""
        # Get plugin permissions from manifest
        plugin_permissions = plugin_manifest.get("permissions", [])

        # Check if plugin has required permissions
        for permission in requested_permissions:
            if permission not in plugin_permissions:
                return False, f"Plugin does not have required permission: {permission}"

        return True, "Plugin permissions verified"

    def shutdown(self):
        """Shutdown the security manager."""
        # Close database connection
        if self.conn:
            self.conn.close()
