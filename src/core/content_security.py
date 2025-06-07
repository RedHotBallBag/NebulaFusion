#!/usr/bin/env python3
# NebulaFusion Browser - Content Security Manager

import os
import sys
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

class ContentSecurityManager(QObject):
    """
    Manager for content security policies and protections.
    Handles content security policies, safe browsing, and content filtering.
    """
    
    # Signals
    threat_detected = pyqtSignal(str, str)  # url, threat_type
    content_blocked = pyqtSignal(str, str)  # url, reason
    
    def __init__(self, app_controller):
        """Initialize the content security manager."""
        super().__init__()
        self.app_controller = app_controller
        
        # Blocklists
        self.malware_domains = set()
        self.phishing_domains = set()
        self.ad_domains = set()
        self.tracker_domains = set()
        
        # Content filters
        self.content_filters = {}
        
        # Initialize content security
        self.initialized = False
    
    def initialize(self):
        """Initialize the content security manager."""
        self.app_controller.logger.info("Initializing content security manager...")
        
        # Load blocklists
        self._load_blocklists()
        
        # Register default content filters
        self._register_default_filters()
        
        # Update state
        self.initialized = True
        
        self.app_controller.logger.info("Content security manager initialized.")
        
        return True
    
    def cleanup(self):
        """Clean up the content security manager."""
        self.app_controller.logger.info("Cleaning up content security manager...")
        
        # Clear blocklists
        self.malware_domains.clear()
        self.phishing_domains.clear()
        self.ad_domains.clear()
        self.tracker_domains.clear()
        
        # Clear content filters
        self.content_filters.clear()
        
        # Update state
        self.initialized = False
        
        self.app_controller.logger.info("Content security manager cleaned up.")
        
        return True
    
    def _load_blocklists(self):
        """Load blocklists."""
        try:
            # Create blocklists directory
            blocklists_dir = os.path.expanduser("~/.nebulafusion/blocklists")
            os.makedirs(blocklists_dir, exist_ok=True)
            
            # Load malware domains
            malware_path = os.path.join(blocklists_dir, "malware.txt")
            if os.path.exists(malware_path):
                with open(malware_path, "r") as f:
                    self.malware_domains = set(line.strip() for line in f if line.strip())
            
            # Load phishing domains
            phishing_path = os.path.join(blocklists_dir, "phishing.txt")
            if os.path.exists(phishing_path):
                with open(phishing_path, "r") as f:
                    self.phishing_domains = set(line.strip() for line in f if line.strip())
            
            # Load ad domains
            ad_path = os.path.join(blocklists_dir, "ads.txt")
            if os.path.exists(ad_path):
                with open(ad_path, "r") as f:
                    self.ad_domains = set(line.strip() for line in f if line.strip())
            
            # Load tracker domains
            tracker_path = os.path.join(blocklists_dir, "trackers.txt")
            if os.path.exists(tracker_path):
                with open(tracker_path, "r") as f:
                    self.tracker_domains = set(line.strip() for line in f if line.strip())
            
            self.app_controller.logger.info(f"Loaded blocklists: {len(self.malware_domains)} malware, {len(self.phishing_domains)} phishing, {len(self.ad_domains)} ads, {len(self.tracker_domains)} trackers")
        
        except Exception as e:
            self.app_controller.logger.error(f"Error loading blocklists: {e}")
    
    def _register_default_filters(self):
        """Register default content filters."""
        # Register malware filter
        self.register_content_filter("malware", self._filter_malware)
        
        # Register phishing filter
        self.register_content_filter("phishing", self._filter_phishing)
        
        # Register ad filter
        self.register_content_filter("ads", self._filter_ads)
        
        # Register tracker filter
        self.register_content_filter("trackers", self._filter_trackers)
    
    def register_content_filter(self, filter_id, filter_func):
        """Register a content filter."""
        self.content_filters[filter_id] = filter_func
        self.app_controller.logger.info(f"Registered content filter: {filter_id}")
        return True
    
    def unregister_content_filter(self, filter_id):
        """Unregister a content filter."""
        if filter_id in self.content_filters:
            del self.content_filters[filter_id]
            self.app_controller.logger.info(f"Unregistered content filter: {filter_id}")
            return True
        return False
    
    def check_url(self, url):
        """Check if a URL is safe."""
        # Get URL domain
        domain = self._get_domain(url)
        
        # Check all filters
        for filter_id, filter_func in self.content_filters.items():
            result = filter_func(url, domain)
            if result:
                return False, filter_id
        
        return True, None
    
    def _filter_malware(self, url, domain):
        """Filter malware domains."""
        if domain in self.malware_domains:
            self.threat_detected.emit(url, "malware")
            self.app_controller.hook_registry.trigger_hook("onThreatDetected", url, "malware")
            self.app_controller.logger.warning(f"Malware detected: {url}")
            return True
        return False
    
    def _filter_phishing(self, url, domain):
        """Filter phishing domains."""
        if domain in self.phishing_domains:
            self.threat_detected.emit(url, "phishing")
            self.app_controller.hook_registry.trigger_hook("onThreatDetected", url, "phishing")
            self.app_controller.logger.warning(f"Phishing detected: {url}")
            return True
        return False
    
    def _filter_ads(self, url, domain):
        """Filter ad domains."""
        if domain in self.ad_domains:
            self.content_blocked.emit(url, "ad")
            self.app_controller.hook_registry.trigger_hook("onContentBlocked", url, "ad")
            self.app_controller.logger.info(f"Ad blocked: {url}")
            return True
        return False
    
    def _filter_trackers(self, url, domain):
        """Filter tracker domains."""
        if domain in self.tracker_domains:
            self.content_blocked.emit(url, "tracker")
            self.app_controller.hook_registry.trigger_hook("onContentBlocked", url, "tracker")
            self.app_controller.logger.info(f"Tracker blocked: {url}")
            return True
        return False
    
    def _get_domain(self, url):
        """Get domain from URL."""
        try:
            # Parse URL
            qurl = QUrl(url)
            
            # Get domain
            domain = qurl.host()
            
            # Remove www prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            return domain
        
        except Exception as e:
            self.app_controller.logger.error(f"Error getting domain from URL: {e}")
            return ""
    
    def add_to_blocklist(self, domain, blocklist_type):
        """Add a domain to a blocklist."""
        try:
            # Check blocklist type
            if blocklist_type == "malware":
                self.malware_domains.add(domain)
            elif blocklist_type == "phishing":
                self.phishing_domains.add(domain)
            elif blocklist_type == "ads":
                self.ad_domains.add(domain)
            elif blocklist_type == "trackers":
                self.tracker_domains.add(domain)
            else:
                self.app_controller.logger.warning(f"Unknown blocklist type: {blocklist_type}")
                return False
            
            # Save blocklist
            self._save_blocklist(blocklist_type)
            
            self.app_controller.logger.info(f"Added {domain} to {blocklist_type} blocklist")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error adding to blocklist: {e}")
            return False
    
    def remove_from_blocklist(self, domain, blocklist_type):
        """Remove a domain from a blocklist."""
        try:
            # Check blocklist type
            if blocklist_type == "malware":
                self.malware_domains.discard(domain)
            elif blocklist_type == "phishing":
                self.phishing_domains.discard(domain)
            elif blocklist_type == "ads":
                self.ad_domains.discard(domain)
            elif blocklist_type == "trackers":
                self.tracker_domains.discard(domain)
            else:
                self.app_controller.logger.warning(f"Unknown blocklist type: {blocklist_type}")
                return False
            
            # Save blocklist
            self._save_blocklist(blocklist_type)
            
            self.app_controller.logger.info(f"Removed {domain} from {blocklist_type} blocklist")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error removing from blocklist: {e}")
            return False
    
    def _save_blocklist(self, blocklist_type):
        """Save a blocklist."""
        try:
            # Create blocklists directory
            blocklists_dir = os.path.expanduser("~/.nebulafusion/blocklists")
            os.makedirs(blocklists_dir, exist_ok=True)
            
            # Get blocklist
            if blocklist_type == "malware":
                blocklist = self.malware_domains
                filename = "malware.txt"
            elif blocklist_type == "phishing":
                blocklist = self.phishing_domains
                filename = "phishing.txt"
            elif blocklist_type == "ads":
                blocklist = self.ad_domains
                filename = "ads.txt"
            elif blocklist_type == "trackers":
                blocklist = self.tracker_domains
                filename = "trackers.txt"
            else:
                self.app_controller.logger.warning(f"Unknown blocklist type: {blocklist_type}")
                return False
            
            # Save blocklist
            path = os.path.join(blocklists_dir, filename)
            with open(path, "w") as f:
                for domain in sorted(blocklist):
                    f.write(f"{domain}\n")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error saving blocklist: {e}")
            return False
    
    def import_blocklist(self, file_path, blocklist_type):
        """Import a blocklist from a file."""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self.app_controller.logger.warning(f"File not found: {file_path}")
                return False
            
            # Read domains
            with open(file_path, "r") as f:
                domains = set(line.strip() for line in f if line.strip())
            
            # Add domains to blocklist
            for domain in domains:
                self.add_to_blocklist(domain, blocklist_type)
            
            self.app_controller.logger.info(f"Imported {len(domains)} domains to {blocklist_type} blocklist")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error importing blocklist: {e}")
            return False
    
    def export_blocklist(self, file_path, blocklist_type):
        """Export a blocklist to a file."""
        try:
            # Get blocklist
            if blocklist_type == "malware":
                blocklist = self.malware_domains
            elif blocklist_type == "phishing":
                blocklist = self.phishing_domains
            elif blocklist_type == "ads":
                blocklist = self.ad_domains
            elif blocklist_type == "trackers":
                blocklist = self.tracker_domains
            else:
                self.app_controller.logger.warning(f"Unknown blocklist type: {blocklist_type}")
                return False
            
            # Create directory
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save blocklist
            with open(file_path, "w") as f:
                for domain in sorted(blocklist):
                    f.write(f"{domain}\n")
            
            self.app_controller.logger.info(f"Exported {len(blocklist)} domains from {blocklist_type} blocklist")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error exporting blocklist: {e}")
            return False
    
    def clear_blocklist(self, blocklist_type):
        """Clear a blocklist."""
        try:
            # Check blocklist type
            if blocklist_type == "malware":
                self.malware_domains.clear()
            elif blocklist_type == "phishing":
                self.phishing_domains.clear()
            elif blocklist_type == "ads":
                self.ad_domains.clear()
            elif blocklist_type == "trackers":
                self.tracker_domains.clear()
            else:
                self.app_controller.logger.warning(f"Unknown blocklist type: {blocklist_type}")
                return False
            
            # Save blocklist
            self._save_blocklist(blocklist_type)
            
            self.app_controller.logger.info(f"Cleared {blocklist_type} blocklist")
            
            return True
        
        except Exception as e:
            self.app_controller.logger.error(f"Error clearing blocklist: {e}")
            return False
