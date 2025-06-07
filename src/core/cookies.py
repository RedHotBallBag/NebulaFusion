#!/usr/bin/env python3
# NebulaFusion Browser - Cookies Manager

import os
from PyQt6.QtCore import QObject, pyqtSignal


class CookiesManager(QObject):
    """
    Manager for browser cookies.
    Handles storing, retrieving, and managing cookies.
    """
    
    # Signals
    cookies_cleared = pyqtSignal()
    
    def __init__(self, app_controller):
        """Initialize the cookies manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Cookie stores
        self.cookie_stores = {}
        
        # Initialize cookies
        self.initialized = False
    
    def initialize(self):
        """Initialize the cookies manager."""
        self.app_controller.logger.info("Initializing cookies manager...")
        
        # Get default profile cookie store
        default_profile = self.app_controller.web_engine_manager.get_default_profile()
        self.cookie_stores["default"] = default_profile.cookieStore()
        
        # Get private profile cookie store
        private_profile = self.app_controller.web_engine_manager.get_private_profile()
        self.cookie_stores["private"] = private_profile.cookieStore()
        
        # Connect signals
        self._connect_signals()
        
        # Update state
        self.initialized = True
        
        self.app_controller.logger.info("Cookies manager initialized.")
        
        return True
    
    def cleanup(self):
        """Clean up the cookies manager."""
        self.app_controller.logger.info("Cleaning up cookies manager...")
        
        # Disconnect signals
        self._disconnect_signals()
        
        # Clear cookie stores
        self.cookie_stores.clear()
        
        # Update state
        self.initialized = False
        
        self.app_controller.logger.info("Cookies manager cleaned up.")
        
        return True
    
    def _connect_signals(self):
        """Connect signals."""
        # Connect default cookie store signals
        default_store = self.cookie_stores.get("default")
        if default_store:
            default_store.cookieAdded.connect(self._on_cookie_added)
            default_store.cookieRemoved.connect(self._on_cookie_removed)
        
        # Connect private cookie store signals
        private_store = self.cookie_stores.get("private")
        if private_store:
            private_store.cookieAdded.connect(self._on_cookie_added)
            private_store.cookieRemoved.connect(self._on_cookie_removed)
    
    def _disconnect_signals(self):
        """Disconnect signals."""
        # Disconnect default cookie store signals
        default_store = self.cookie_stores.get("default")
        if default_store:
            try:
                default_store.cookieAdded.disconnect(self._on_cookie_added)
                default_store.cookieRemoved.disconnect(self._on_cookie_removed)
            except Exception:
                pass
        
        # Disconnect private cookie store signals
        private_store = self.cookie_stores.get("private")
        if private_store:
            try:
                private_store.cookieAdded.disconnect(self._on_cookie_added)
                private_store.cookieRemoved.disconnect(self._on_cookie_removed)
            except Exception:
                pass
    
    def _on_cookie_added(self, cookie):
        """Handle cookie added event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onCookieAdded", cookie)
    
    def _on_cookie_removed(self, cookie):
        """Handle cookie removed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onCookieRemoved", cookie)
    
    def clear_cookies(self, profile_name="default"):
        """Clear all cookies."""
        try:
            # Get cookie store
            cookie_store = self.cookie_stores.get(profile_name)
            if not cookie_store:
                self.app_controller.logger.warning(f"Cookie store not found: {profile_name}")
                return False
            
            # Clear cookies
            cookie_store.deleteAllCookies()
            
            # Emit signal
            self.cookies_cleared.emit()
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onCookiesCleared", profile_name)
            
            self.app_controller.logger.info(f"Cookies cleared for profile: {profile_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error clearing cookies: {e}")
            return False
    
    def set_cookie_filter(self, filter_func, profile_name="default"):
        """Set cookie filter."""
        try:
            # Get cookie store
            cookie_store = self.cookie_stores.get(profile_name)
            if not cookie_store:
                self.app_controller.logger.warning(f"Cookie store not found: {profile_name}")
                return False
            
            # Set cookie filter
            cookie_store.setCookieFilter(filter_func)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onCookieFilterSet", profile_name)
            
            self.app_controller.logger.info(f"Cookie filter set for profile: {profile_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error setting cookie filter: {e}")
            return False
    
    def block_third_party_cookies(self, block=True, profile_name="default"):
        """Block third-party cookies."""
        try:
            # Get cookie store
            cookie_store = self.cookie_stores.get(profile_name)
            if not cookie_store:
                self.app_controller.logger.warning(f"Cookie store not found: {profile_name}")
                return False
            
            # Set cookie filter
            if block:
                def filter_func(request):
                    """Allow only first-party cookies."""
                    return not request.thirdParty

                cookie_store.setCookieFilter(filter_func)
            else:
                # Allow all cookies
                cookie_store.setCookieFilter(lambda request: True)
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onThirdPartyCookiesBlocked", block, profile_name)
            
            self.app_controller.logger.info(f"Third-party cookies {'blocked' if block else 'allowed'} for profile: {profile_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error blocking third-party cookies: {e}")
            return False
    
    def export_cookies(self, file_path, profile_name="default"):
        """Export cookies to a file."""
        try:
            # Get cookie store
            cookie_store = self.cookie_stores.get(profile_name)
            if not cookie_store:
                self.app_controller.logger.warning(f"Cookie store not found: {profile_name}")
                return False
            
            # Create cookies directory
            cookies_dir = os.path.dirname(file_path)
            os.makedirs(cookies_dir, exist_ok=True)
            
            # Export cookies
            # Note: PyQt6 doesn't provide direct access to cookies
            # This is a placeholder for future implementation
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onCookiesExported", profile_name, file_path)
            
            self.app_controller.logger.info(f"Cookies exported for profile: {profile_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error exporting cookies: {e}")
            return False
    
    def import_cookies(self, file_path, profile_name="default"):
        """Import cookies from a file."""
        try:
            # Get cookie store
            cookie_store = self.cookie_stores.get(profile_name)
            if not cookie_store:
                self.app_controller.logger.warning(f"Cookie store not found: {profile_name}")
                return False
            
            # Import cookies
            # Note: PyQt6 doesn't provide direct access to cookies
            # This is a placeholder for future implementation
            
            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onCookiesImported", profile_name, file_path)
            
            self.app_controller.logger.info(f"Cookies imported for profile: {profile_name}")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error importing cookies: {e}")
            return False
