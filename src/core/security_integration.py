#!/usr/bin/env python3
# NebulaFusion Browser - Security Integration

import os
import sys
import json
import time
import inspect
import traceback
from PyQt5.QtCore import QObject, pyqtSignal

class SecurityIntegration(QObject):
    """
    Integrates security features across browser modules.
    """
    
    # Signals
    security_violation = pyqtSignal(str, str, str)
    permission_denied = pyqtSignal(str, str, str)
    
    def __init__(self, app_controller):
        """Initialize the security integration."""
        super().__init__()
        self.app_controller = app_controller
        
        # Security hooks
        self.security_hooks = {}
        
        # Permission cache
        self.permission_cache = {}
    
    def initialize(self):
        """Initialize the security integration."""
        # Register security hooks
        self._register_security_hooks()
        
        # Connect signals
        self._connect_signals()
    
    def _register_security_hooks(self):
        """Register security hooks."""
        # Tab hooks
        self.security_hooks["beforeTabCreated"] = self._hook_before_tab_created
        self.security_hooks["beforeTabClosed"] = self._hook_before_tab_closed
        
        # Navigation hooks
        self.security_hooks["beforeNavigation"] = self._hook_before_navigation
        self.security_hooks["beforeResourceLoad"] = self._hook_before_resource_load
        
        # Content hooks
        self.security_hooks["beforeScriptExecution"] = self._hook_before_script_execution
        self.security_hooks["beforeDOMModification"] = self._hook_before_dom_modification
        
        # Cookie hooks
        self.security_hooks["beforeCookieSet"] = self._hook_before_cookie_set
        self.security_hooks["beforeCookieRead"] = self._hook_before_cookie_read
        
        # Download hooks
        self.security_hooks["beforeDownload"] = self._hook_before_download
        
        # Plugin hooks
        self.security_hooks["beforePluginLoad"] = self._hook_before_plugin_load
        self.security_hooks["beforePluginAPICall"] = self._hook_before_plugin_api_call
        self.security_hooks["beforePluginHookExecution"] = self._hook_before_plugin_hook_execution
        
        # Register hooks with hook registry
        for hook_name, callback in self.security_hooks.items():
            self.app_controller.hook_registry.register_hook(hook_name, "security_integration", callback)
    
    def _connect_signals(self):
        """Connect signals."""
        # Connect to plugin loader signals
        self.app_controller.plugin_loader.plugin_loaded.connect(self._on_plugin_loaded)
        self.app_controller.plugin_loader.plugin_load_failed.connect(self._on_plugin_load_failed)
        
        # Connect to plugin API signals
        for plugin_id, plugin_api in self.app_controller.plugin_manager.plugin_apis.items():
            self._connect_plugin_api_signals(plugin_id, plugin_api)
        
        # Connect to sandbox signals
        for plugin_id, sandbox in self.app_controller.plugin_manager.plugin_sandboxes.items():
            self._connect_sandbox_signals(plugin_id, sandbox)
    
    def _connect_plugin_api_signals(self, plugin_id, plugin_api):
        """Connect to plugin API signals."""
        # This would typically connect to plugin API signals
        # For now, just log the connection
        self.app_controller.logger.debug(f"Connected to plugin API signals for {plugin_id}")
    
    def _connect_sandbox_signals(self, plugin_id, sandbox):
        """Connect to sandbox signals."""
        # Connect to sandbox signals
        sandbox.resource_limit_exceeded.connect(
            lambda resource, value: self._on_resource_limit_exceeded(plugin_id, resource, value))
        sandbox.security_violation.connect(
            lambda message: self._on_security_violation(plugin_id, message))
    
    def _on_plugin_loaded(self, plugin_id, plugin_instance):
        """Handle plugin loaded event."""
        # Log plugin loaded
        self.app_controller.logger.info(f"Plugin loaded: {plugin_id}")
        
        # Connect to plugin API signals
        plugin_api = self.app_controller.plugin_manager.get_plugin_api(plugin_id)
        self._connect_plugin_api_signals(plugin_id, plugin_api)
        
        # Connect to sandbox signals
        if plugin_id in self.app_controller.plugin_manager.plugin_sandboxes:
            sandbox = self.app_controller.plugin_manager.plugin_sandboxes[plugin_id]
            self._connect_sandbox_signals(plugin_id, sandbox)
    
    def _on_plugin_load_failed(self, plugin_id, error):
        """Handle plugin load failed event."""
        # Log plugin load failed
        self.app_controller.logger.error(f"Plugin load failed: {plugin_id} - {error}")
    
    def _on_resource_limit_exceeded(self, plugin_id, resource, value):
        """Handle resource limit exceeded event."""
        # Log resource limit exceeded
        self.app_controller.logger.warning(
            f"Plugin {plugin_id} exceeded {resource} limit: {value}")
        
        # Emit signal
        self.security_violation.emit(
            plugin_id,
            "resource_limit_exceeded",
            f"Exceeded {resource} limit: {value}"
        )
        
        # Take action based on resource
        if resource == "cpu_percent" and value > 50:
            # Disable plugin if CPU usage is extremely high
            self.app_controller.plugin_manager.disable_plugin(plugin_id)
            self.app_controller.logger.warning(
                f"Plugin {plugin_id} disabled due to excessive CPU usage: {value}%")
    
    def _on_security_violation(self, plugin_id, message):
        """Handle security violation event."""
        # Log security violation
        self.app_controller.logger.warning(
            f"Plugin {plugin_id} security violation: {message}")
        
        # Emit signal
        self.security_violation.emit(
            plugin_id,
            "security_violation",
            message
        )
    
    def check_permission(self, plugin_id, permission):
        """Check if a plugin has a permission."""
        # Check cache
        cache_key = f"{plugin_id}:{permission}"
        if cache_key in self.permission_cache:
            return self.permission_cache[cache_key]
        
        # Get plugin information
        plugin_info = self.app_controller.plugin_loader.get_plugin(plugin_id)
        if not plugin_info:
            return False
        
        # Get plugin permissions
        permissions = plugin_info["manifest"].get("permissions", [])
        
        # Check permission
        has_permission = permission in permissions or "all" in permissions
        
        # Cache result
        self.permission_cache[cache_key] = has_permission
        
        return has_permission
    
    def request_permission(self, plugin_id, permission, reason=None):
        """Request a permission for a plugin."""
        # Check if plugin already has permission
        if self.check_permission(plugin_id, permission):
            return True
        
        # Get plugin information
        plugin_info = self.app_controller.plugin_loader.get_plugin(plugin_id)
        if not plugin_info:
            return False
        
        # Get plugin name
        plugin_name = plugin_info["manifest"].get("name", plugin_id)
        
        # This would typically show a permission request dialog
        # For now, just log the request and deny it
        self.app_controller.logger.warning(
            f"Plugin {plugin_name} requested permission {permission}: {reason}")
        
        # Emit signal
        self.permission_denied.emit(
            plugin_id,
            permission,
            reason or "Permission not granted"
        )
        
        return False
    
    def _hook_before_tab_created(self, *args, **kwargs):
        """Hook before tab created."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "tabs"):
            self.permission_denied.emit(
                plugin_id,
                "tabs",
                "Permission denied to create tab"
            )
            return False
        
        return True
    
    def _hook_before_tab_closed(self, *args, **kwargs):
        """Hook before tab closed."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "tabs"):
            self.permission_denied.emit(
                plugin_id,
                "tabs",
                "Permission denied to close tab"
            )
            return False
        
        return True
    
    def _hook_before_navigation(self, url, *args, **kwargs):
        """Hook before navigation."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "navigation"):
            self.permission_denied.emit(
                plugin_id,
                "navigation",
                f"Permission denied to navigate to {url}"
            )
            return False
        
        # Check URL security
        security_status = self.app_controller.security_manager.check_url_security(url)
        if not security_status["is_secure"]:
            self.security_violation.emit(
                plugin_id,
                "navigation",
                f"Navigation to insecure URL blocked: {url}"
            )
            return False
        
        return True
    
    def _hook_before_resource_load(self, url, resource_type, *args, **kwargs):
        """Hook before resource load."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "content"):
            self.permission_denied.emit(
                plugin_id,
                "content",
                f"Permission denied to load resource {url}"
            )
            return False
        
        # Check URL security
        security_status = self.app_controller.security_manager.check_url_security(url)
        if not security_status["is_secure"]:
            self.security_violation.emit(
                plugin_id,
                "resource_load",
                f"Loading insecure resource blocked: {url}"
            )
            return False
        
        return True
    
    def _hook_before_script_execution(self, script, url, *args, **kwargs):
        """Hook before script execution."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "content"):
            self.permission_denied.emit(
                plugin_id,
                "content",
                f"Permission denied to execute script on {url}"
            )
            return False
        
        # This would typically check script content for malicious code
        # For now, just return True
        return True
    
    def _hook_before_dom_modification(self, element, modification, *args, **kwargs):
        """Hook before DOM modification."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "content"):
            self.permission_denied.emit(
                plugin_id,
                "content",
                f"Permission denied to modify DOM"
            )
            return False
        
        # This would typically check DOM modification for security issues
        # For now, just return True
        return True
    
    def _hook_before_cookie_set(self, cookie, *args, **kwargs):
        """Hook before cookie set."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "cookies"):
            self.permission_denied.emit(
                plugin_id,
                "cookies",
                f"Permission denied to set cookie"
            )
            return False
        
        # This would typically check cookie for security issues
        # For now, just return True
        return True
    
    def _hook_before_cookie_read(self, domain, name, *args, **kwargs):
        """Hook before cookie read."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "cookies"):
            self.permission_denied.emit(
                plugin_id,
                "cookies",
                f"Permission denied to read cookie"
            )
            return False
        
        # This would typically check cookie access for security issues
        # For now, just return True
        return True
    
    def _hook_before_download(self, url, path, *args, **kwargs):
        """Hook before download."""
        # Get plugin ID from context
        plugin_id = kwargs.get("plugin_id")
        if not plugin_id:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, "downloads"):
            self.permission_denied.emit(
                plugin_id,
                "downloads",
                f"Permission denied to download file"
            )
            return False
        
        # Check URL security
        security_status = self.app_controller.security_manager.check_url_security(url)
        if not security_status["is_secure"]:
            self.security_violation.emit(
                plugin_id,
                "download",
                f"Download from insecure URL blocked: {url}"
            )
            return False
        
        # This would typically check download path for security issues
        # For now, just return True
        return True
    
    def _hook_before_plugin_load(self, plugin_path, *args, **kwargs):
        """Hook before plugin load."""
        # This would typically check plugin for security issues
        # For now, just return True
        return True
    
    def _hook_before_plugin_api_call(self, plugin_id, method_name, *args, **kwargs):
        """Hook before plugin API call."""
        # Get required permission for method
        permission = self._get_permission_for_api_method(method_name)
        if not permission:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, permission):
            self.permission_denied.emit(
                plugin_id,
                permission,
                f"Permission denied to call API method {method_name}"
            )
            return False
        
        return True
    
    def _hook_before_plugin_hook_execution(self, hook_name, plugin_id, *args, **kwargs):
        """Hook before plugin hook execution."""
        # Get required permission for hook
        permission = self._get_permission_for_hook(hook_name)
        if not permission:
            return True
        
        # Check permission
        if not self.check_permission(plugin_id, permission):
            self.permission_denied.emit(
                plugin_id,
                permission,
                f"Permission denied to execute hook {hook_name}"
            )
            return False
        
        return True
    
    def _get_permission_for_api_method(self, method_name):
        """Get required permission for an API method."""
        # Map API methods to permissions
        method_permissions = {
            # Browser API
            "get_browser_info": "browser",
            "get_version": "browser",
            "restart": "browser",
            "exit": "browser",
            
            # Tab API
            "get_tabs": "tabs",
            "get_current_tab": "tabs",
            "create_tab": "tabs",
            "close_tab": "tabs",
            "select_tab": "tabs",
            "move_tab": "tabs",
            "get_tab_info": "tabs",
            
            # Navigation API
            "navigate": "navigation",
            "go_back": "navigation",
            "go_forward": "navigation",
            "reload": "navigation",
            "stop": "navigation",
            "get_current_url": "navigation",
            
            # Content API
            "get_page_html": "content",
            "get_page_dom": "content",
            "inject_css": "content",
            "inject_js": "content",
            "modify_dom": "content",
            
            # UI API
            "add_toolbar_button": "ui",
            "add_menu_item": "ui",
            "add_context_menu_item": "ui",
            "show_notification": "ui",
            "create_panel": "ui",
            
            # Data API
            "get_bookmarks": "bookmarks",
            "add_bookmark": "bookmarks",
            "remove_bookmark": "bookmarks",
            "get_history": "history",
            "clear_history": "history",
            "get_cookies": "cookies",
            "set_cookie": "cookies",
            "remove_cookie": "cookies",
            
            # Download API
            "download_file": "downloads",
            "pause_download": "downloads",
            "resume_download": "downloads",
            "cancel_download": "downloads",
            "get_downloads": "downloads",
            
            # Settings API
            "get_browser_settings": "settings",
            "register_settings_page": "settings",
            
            # Unique Features API
            "start_reality_augmentation": "reality_augmentation",
            "start_collaborative_session": "collaborative",
            "transform_content": "content_transform",
            "take_time_snapshot": "time_travel",
            "organize_dimensional_tabs": "dimensional_tabs",
            "register_voice_command": "voice_commands"
        }
        
        return method_permissions.get(method_name)
    
    def _get_permission_for_hook(self, hook_name):
        """Get required permission for a hook."""
        # Map hooks to permissions
        hook_permissions = {
            # Browser lifecycle hooks
            "onBrowserStart": "browser",
            "onBrowserExit": "browser",
            "onSettingsChanged": "settings",
            
            # Tab hooks
            "onTabCreated": "tabs",
            "beforeTabClosed": "tabs",
            "onTabClosed": "tabs",
            "onTabSelected": "tabs",
            "onTabMoved": "tabs",
            
            # Navigation hooks
            "beforeNavigation": "navigation",
            "afterNavigation": "navigation",
            "onPageStartLoad": "navigation",
            "onPageLoadProgress": "navigation",
            "onPageFinishLoad": "navigation",
            "onPageError": "navigation",
            
            # Content hooks
            "beforeDOMLoad": "content",
            "afterDOMLoad": "content",
            "onHTMLModify": "content",
            "onCSSModify": "content",
            "onJSExecute": "content",
            
            # UI hooks
            "onToolbarCreated": "ui",
            "onMenuCreated": "ui",
            "onContextMenu": "ui",
            "onStatusBarUpdate": "ui",
            "onAddressBarUpdate": "ui",
            
            # Data hooks
            "onBookmarkAdded": "bookmarks",
            "onBookmarkRemoved": "bookmarks",
            "onHistoryAdded": "history",
            "onHistoryRemoved": "history",
            "onCookieSet": "cookies",
            "onCookieRemoved": "cookies",
            "onCookiesCleared": "cookies",
            
            # Download hooks
            "onDownloadStart": "downloads",
            "onDownloadProgress": "downloads",
            "onDownloadComplete": "downloads",
            "onDownloadError": "downloads",
            "onDownloadCanceled": "downloads",
            
            # Unique feature hooks
            "onRealityAugmentation": "reality_augmentation",
            "onCollaborativeSession": "collaborative",
            "onContentTransform": "content_transform",
            "onTimeTravelSnapshot": "time_travel",
            "onDimensionalTabChange": "dimensional_tabs",
            "onVoiceCommand": "voice_commands"
        }
        
        return hook_permissions.get(hook_name)
    
    def clear_permission_cache(self):
        """Clear permission cache."""
        self.permission_cache.clear()
    
    def clear_permission_cache_for_plugin(self, plugin_id):
        """Clear permission cache for a plugin."""
        keys_to_remove = [key for key in self.permission_cache if key.startswith(f"{plugin_id}:")]
        for key in keys_to_remove:
            del self.permission_cache[key]
