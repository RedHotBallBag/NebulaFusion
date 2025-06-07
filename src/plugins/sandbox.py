#!/usr/bin/env python3
# NebulaFusion Browser - Plugin Sandbox

import os
import sys
import json
import time
import threading
import resource
import traceback
from PyQt5.QtCore import QObject, pyqtSignal

class PluginSandbox(QObject):
    """
    Enforces security boundaries for plugin execution.
    """
    
    # Signals
    resource_limit_exceeded = pyqtSignal(str, str, float)
    security_violation = pyqtSignal(str, str)
    
    def __init__(self, app_controller, plugin_id):
        """Initialize the plugin sandbox."""
        super().__init__()
        self.app_controller = app_controller
        self.plugin_id = plugin_id
        
        # Resource usage tracking
        self.resource_usage = {
            "cpu_time": 0,
            "memory": 0,
            "api_calls": 0,
            "network_requests": 0,
            "file_access": 0
        }
        
        # Resource limits
        self.resource_limits = {
            "cpu_percent": self.app_controller.settings_manager.get_setting(
                "security_plugin_cpu_percent", 10),
            "memory_mb": self.app_controller.settings_manager.get_setting(
                "security_plugin_memory_mb", 100),
            "network_requests_per_minute": self.app_controller.settings_manager.get_setting(
                "security_plugin_network_requests_per_minute", 60),
            "file_access_paths": self.app_controller.settings_manager.get_setting(
                "security_plugin_file_access_paths", ["~/.nebulafusion/plugins"])
        }
        
        # API call log
        self.api_call_log = []
        
        # Network request log
        self.network_request_log = []
        
        # File access log
        self.file_access_log = []
        
        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_resources)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def log_api_call(self, method_name, args, kwargs):
        """Log an API call."""
        # Record API call
        self.api_call_log.append({
            "method": method_name,
            "timestamp": time.time(),
            "args_count": len(args),
            "kwargs_count": len(kwargs)
        })
        
        # Update resource usage
        self.resource_usage["api_calls"] += 1
    
    def log_network_request(self, url, method="GET"):
        """Log a network request."""
        # Record network request
        self.network_request_log.append({
            "url": url,
            "method": method,
            "timestamp": time.time()
        })
        
        # Update resource usage
        self.resource_usage["network_requests"] += 1
        
        # Check network request limit
        self._check_network_request_limit()
    
    def log_file_access(self, path, mode="r"):
        """Log a file access."""
        # Record file access
        self.file_access_log.append({
            "path": path,
            "mode": mode,
            "timestamp": time.time()
        })
        
        # Update resource usage
        self.resource_usage["file_access"] += 1
        
        # Check file access permission
        return self._check_file_access_permission(path, mode)
    
    def _check_network_request_limit(self):
        """Check if network request limit is exceeded."""
        # Get requests in the last minute
        current_time = time.time()
        requests_last_minute = [
            req for req in self.network_request_log
            if req["timestamp"] > current_time - 60
        ]
        
        # Check limit
        if len(requests_last_minute) > self.resource_limits["network_requests_per_minute"]:
            # Log violation
            self.app_controller.logger.warning(
                f"Plugin {self.plugin_id} exceeded network request limit: "
                f"{len(requests_last_minute)} requests in the last minute"
            )
            
            # Emit signal
            self.resource_limit_exceeded.emit(
                self.plugin_id,
                "network_requests_per_minute",
                len(requests_last_minute)
            )
            
            return False
        
        return True
    
    def _check_file_access_permission(self, path, mode):
        """Check if file access is permitted."""
        # Normalize path
        path = os.path.abspath(os.path.expanduser(path))
        
        # Check if path is in allowed paths
        allowed = False
        for allowed_path in self.resource_limits["file_access_paths"]:
            allowed_path = os.path.abspath(os.path.expanduser(allowed_path))
            if path.startswith(allowed_path):
                allowed = True
                break
        
        # Check write permission
        if mode in ("w", "a", "w+", "a+") and not allowed:
            # Log violation
            self.app_controller.logger.warning(
                f"Plugin {self.plugin_id} attempted unauthorized file write: {path}"
            )
            
            # Emit signal
            self.security_violation.emit(
                self.plugin_id,
                f"Unauthorized file write: {path}"
            )
            
            return False
        
        # Check read permission for sensitive files
        sensitive_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "~/.ssh",
            "~/.nebulafusion/settings.json"
        ]
        
        for sensitive_path in sensitive_paths:
            sensitive_path = os.path.abspath(os.path.expanduser(sensitive_path))
            if path.startswith(sensitive_path) and not allowed:
                # Log violation
                self.app_controller.logger.warning(
                    f"Plugin {self.plugin_id} attempted unauthorized access to sensitive file: {path}"
                )
                
                # Emit signal
                self.security_violation.emit(
                    self.plugin_id,
                    f"Unauthorized access to sensitive file: {path}"
                )
                
                return False
        
        return True
    
    def _monitor_resources(self):
        """Monitor plugin resource usage."""
        while self.monitoring_active:
            try:
                # Get plugin process info
                # In a real implementation, we would get the actual process info
                # For now, we'll just simulate resource usage
                
                # Update CPU usage (simulated)
                self.resource_usage["cpu_time"] += 0.1
                
                # Update memory usage (simulated)
                self.resource_usage["memory"] = 50  # MB
                
                # Check CPU limit
                if self.resource_usage["cpu_time"] > self.resource_limits["cpu_percent"]:
                    # Log violation
                    self.app_controller.logger.warning(
                        f"Plugin {self.plugin_id} exceeded CPU limit: "
                        f"{self.resource_usage['cpu_time']}% (limit: {self.resource_limits['cpu_percent']}%)"
                    )
                    
                    # Emit signal
                    self.resource_limit_exceeded.emit(
                        self.plugin_id,
                        "cpu_percent",
                        self.resource_usage["cpu_time"]
                    )
                
                # Check memory limit
                if self.resource_usage["memory"] > self.resource_limits["memory_mb"]:
                    # Log violation
                    self.app_controller.logger.warning(
                        f"Plugin {self.plugin_id} exceeded memory limit: "
                        f"{self.resource_usage['memory']}MB (limit: {self.resource_limits['memory_mb']}MB)"
                    )
                    
                    # Emit signal
                    self.resource_limit_exceeded.emit(
                        self.plugin_id,
                        "memory_mb",
                        self.resource_usage["memory"]
                    )
                
                # Sleep for a bit
                time.sleep(1)
            
            except Exception as e:
                self.app_controller.logger.error(f"Error monitoring plugin resources: {e}")
                self.app_controller.logger.error(traceback.format_exc())
    
    def get_resource_usage(self):
        """Get resource usage."""
        return self.resource_usage
    
    def get_api_call_log(self):
        """Get API call log."""
        return self.api_call_log
    
    def get_network_request_log(self):
        """Get network request log."""
        return self.network_request_log
    
    def get_file_access_log(self):
        """Get file access log."""
        return self.file_access_log
    
    def shutdown(self):
        """Shutdown the sandbox."""
        # Stop monitoring thread
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1)
        
        # Clear logs
        self.api_call_log.clear()
        self.network_request_log.clear()
        self.file_access_log.clear()
