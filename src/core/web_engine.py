#!/usr/bin/env python3
# NebulaFusion Browser - Web Engine Manager

import os
import sys
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineSettings,
    QWebEngineCookieStore,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView


class WebEngine(QWebEngineView):
    """Simple web engine view wrapper used by tests."""

    def __init__(self, parent=None):
        super().__init__(parent)


class WebEngineManager(QObject):
    """
    Manager for web engine functionality.
    Handles profiles, settings, and web engine configuration.
    """

    # Signals
    profile_created = pyqtSignal(str)  # profile_name
    profile_removed = pyqtSignal(str)  # profile_name

    def __init__(self, app_controller):
        """Initialize the web engine manager."""
        super().__init__()
        self.app_controller = app_controller

        # Profiles
        self.profiles = {}

        # Default profile
        self.default_profile = None

        # Private profile
        self.private_profile = None

        # Initialize web engine
        self.initialized = False

    def initialize(self):
        """Initialize the web engine manager."""
        self.app_controller.logger.info("Initializing web engine manager...")

        # Create default profile
        self.default_profile = self.create_profile("default", is_private=False)

        # Create private profile
        self.private_profile = self.create_profile("private", is_private=True)

        # Configure default profile
        self._configure_default_profile()

        # Configure private profile
        self._configure_private_profile()

        # Update state
        self.initialized = True

        self.app_controller.logger.info("Web engine manager initialized.")

        return True

    def cleanup(self):
        """Clean up the web engine manager."""
        self.app_controller.logger.info("Cleaning up web engine manager...")

        # Clear profiles
        self.profiles.clear()

        # Update state
        self.initialized = False

        self.app_controller.logger.info("Web engine manager cleaned up.")

        return True

    def _configure_default_profile(self):
        """Configure default profile."""
        # Get profile
        profile = self.default_profile

        # Configure settings
        settings = profile.settings()

        # Enable JavaScript
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Enable plugins
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        # Enable local storage
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Enable developer tools
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
        )

        # Enable fullscreen
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )

        # Enable PDF viewer
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        # Enable autoload images
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        # Enable WebGL
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        # Enable WebRTC
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False
        )

        # Set default font sizes
        settings.setFontSize(QWebEngineSettings.FontSize.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.FontSize.DefaultFixedFontSize, 13)
        settings.setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, 10)
        settings.setFontSize(QWebEngineSettings.FontSize.MinimumLogicalFontSize, 10)

        # Set default font families
        settings.setFontFamily(QWebEngineSettings.FontFamily.StandardFont, "Arial")
        settings.setFontFamily(QWebEngineSettings.FontFamily.FixedFont, "Courier New")
        settings.setFontFamily(
            QWebEngineSettings.FontFamily.SerifFont, "Times New Roman"
        )
        settings.setFontFamily(QWebEngineSettings.FontFamily.SansSerifFont, "Arial")
        settings.setFontFamily(
            QWebEngineSettings.FontFamily.CursiveFont, "Comic Sans MS"
        )
        settings.setFontFamily(QWebEngineSettings.FontFamily.FantasyFont, "Impact")

        # Configure HTTP cache
        cache_dir = os.path.expanduser("~/.nebulafusion/cache")
        os.makedirs(cache_dir, exist_ok=True)
        profile.setCachePath(cache_dir)
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100 MB

        # Configure persistent storage
        data_dir = os.path.expanduser("~/.nebulafusion/data")
        os.makedirs(data_dir, exist_ok=True)
        profile.setPersistentStoragePath(data_dir)

        # Configure user agent
        user_agent = profile.httpUserAgent()
        user_agent += " NebulaFusion/1.0"
        profile.setHttpUserAgent(user_agent)

        # Configure cookies
        cookie_store = profile.cookieStore()
        cookie_store.setCookieFilter(lambda cookie, url: True)

    def _configure_private_profile(self):
        """Configure private profile."""
        # Get profile
        profile = self.private_profile

        # Configure settings
        settings = profile.settings()

        # Enable JavaScript
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Enable plugins
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        # Enable local storage
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Enable developer tools
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True
        )

        # Enable fullscreen
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True
        )

        # Enable PDF viewer
        settings.setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

        # Enable autoload images
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        # Enable WebGL
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        # Enable WebRTC
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True
        )

        # Set default font sizes
        settings.setFontSize(QWebEngineSettings.FontSize.DefaultFontSize, 16)
        settings.setFontSize(QWebEngineSettings.FontSize.DefaultFixedFontSize, 13)
        settings.setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, 10)
        settings.setFontSize(QWebEngineSettings.FontSize.MinimumLogicalFontSize, 10)

        # Set default font families
        settings.setFontFamily(QWebEngineSettings.FontFamily.StandardFont, "Arial")
        settings.setFontFamily(QWebEngineSettings.FontFamily.FixedFont, "Courier New")
        settings.setFontFamily(
            QWebEngineSettings.FontFamily.SerifFont, "Times New Roman"
        )
        settings.setFontFamily(QWebEngineSettings.FontFamily.SansSerifFont, "Arial")
        settings.setFontFamily(
            QWebEngineSettings.FontFamily.CursiveFont, "Comic Sans MS"
        )
        settings.setFontFamily(QWebEngineSettings.FontFamily.FantasyFont, "Impact")

        # Configure HTTP cache
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.MemoryHttpCache)

        # Configure user agent
        user_agent = profile.httpUserAgent()
        user_agent += " NebulaFusion/1.0 (Private)"
        profile.setHttpUserAgent(user_agent)

        # Configure cookies
        cookie_store = profile.cookieStore()
        cookie_store.setCookieFilter(lambda cookie, url: True)

    def create_profile(self, name, is_private=False):
        """Create a web engine profile."""
        try:
            # Check if profile already exists (for named profiles)
            if not is_private and name in self.profiles:
                self.app_controller.logger.warning(f"Profile already exists: {name}")
                return self.profiles[name]

            if is_private:
                # Off-the-record profiles are typically not named for persistence.
                # If you need to refer to it, you might store it under a generic key.
                # Let's assume "private" is just a logical name for our manager.
                profile = QWebEngineProfile(
                    parent=self.app_controller
                )  # No storageName means off-the-record
                self.profiles["private_instance"] = (
                    profile  # Store it if needed for later reference
                )
            else:
                profile = QWebEngineProfile(name, parent=self.app_controller)
                self.profiles[name] = profile

            # Emit signal (use the logical name for private profiles if needed)
            profile_key_for_signal = "private" if is_private else name
            self.profile_created.emit(profile_key_for_signal)

            # Trigger hook
            self.app_controller.hook_registry.trigger_hook(
                "onProfileCreated", profile_key_for_signal, is_private
            )

            self.app_controller.logger.info(
                f"Profile created: {profile_key_for_signal} (private: {is_private})"
            )

            return profile

        except Exception as e:
            self.app_controller.logger.error(f"Error creating profile: {e}")
            return None

    def remove_profile(self, name):
        """Remove a web engine profile."""
        try:
            # Check if profile exists
            if name not in self.profiles:
                self.app_controller.logger.warning(f"Profile not found: {name}")
                return False

            # Check if profile is default or private
            if name == "default" or name == "private":
                self.app_controller.logger.warning(
                    f"Cannot remove built-in profile: {name}"
                )
                return False

            # Remove profile
            del self.profiles[name]

            # Emit signal
            self.profile_removed.emit(name)

            # Trigger hook
            self.app_controller.hook_registry.trigger_hook("onProfileRemoved", name)

            self.app_controller.logger.info(f"Profile removed: {name}")

            return True

        except Exception as e:
            self.app_controller.logger.error(f"Error removing profile: {e}")
            return False

    def get_profile(self, name):
        """Get a web engine profile."""
        # Check if profile exists
        if name not in self.profiles:
            self.app_controller.logger.warning(f"Profile not found: {name}")
            return None

        return self.profiles[name]

    def get_default_profile(self):
        """Get the default web engine profile."""
        return self.default_profile

    def get_private_profile(self):
        """Get the private web engine profile."""
        return self.private_profile

    def create_page(self, profile_name=None):
        """Create a web engine page."""
        try:
            # Get profile
            if profile_name:
                profile = self.get_profile(profile_name)
                if not profile:
                    self.app_controller.logger.warning(
                        f"Profile not found: {profile_name}"
                    )
                    profile = self.default_profile
            else:
                profile = self.default_profile

            # Create page
            page = QWebEnginePage(profile)

            # Configure page
            self._configure_page(page)

            return page

        except Exception as e:
            self.app_controller.logger.error(f"Error creating page: {e}")
            return None

    def _configure_page(self, page):
        """Configure a web engine page."""
        # Connect signals
        page.loadStarted.connect(lambda: self._on_load_started(page))
        page.loadProgress.connect(
            lambda progress: self._on_load_progress(page, progress)
        )
        page.loadFinished.connect(lambda success: self._on_load_finished(page, success))
        page.urlChanged.connect(lambda url: self._on_url_changed(page, url))
        page.titleChanged.connect(lambda title: self._on_title_changed(page, title))
        page.iconChanged.connect(lambda icon: self._on_icon_changed(page, icon))
        page.fullScreenRequested.connect(
            lambda request: self._on_fullscreen_requested(page, request)
        )
        page.featurePermissionRequested.connect(
            lambda url, feature: self._on_feature_permission_requested(
                page, url, feature
            )
        )
        page.certificateError.connect(
            lambda error: self._on_certificate_error(page, error)
        )
        page.authenticationRequired.connect(
            lambda url, authenticator: self._on_authentication_required(
                page, url, authenticator
            )
        )
        page.proxyAuthenticationRequired.connect(
            lambda url, authenticator, proxy_host: self._on_proxy_authentication_required(
                page, url, authenticator, proxy_host
            )
        )
        page.renderProcessTerminated.connect(
            lambda status, exit_code: self._on_render_process_terminated(
                page, status, exit_code
            )
        )

    def _on_load_started(self, page):
        """Handle load started event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onPageLoadStarted", page)

    def _on_load_progress(self, page, progress):
        """Handle load progress event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageLoadProgress", page, progress
        )

    def _on_load_finished(self, page, success):
        """Handle load finished event."""
        # Get URL
        url = page.url().toString()

        # Get title
        title = page.title()

        # Add to history
        if success and url and not url.startswith("about:"):
            self.app_controller.history_manager.add_history(url, title)

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageLoadFinished", page, success
        )

    def _on_url_changed(self, page, url):
        """Handle URL changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onPageUrlChanged", page, url)

    def _on_title_changed(self, page, title):
        """Handle title changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageTitleChanged", page, title
        )

    def _on_icon_changed(self, page, icon):
        """Handle icon changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onPageIconChanged", page, icon)

    def _on_fullscreen_requested(self, page, request):
        """Handle fullscreen requested event."""
        # Accept request
        request.accept()

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageFullscreenRequested", page, request.toggleOn()
        )

    def _on_feature_permission_requested(self, page, url, feature):
        """Handle feature permission requested event."""
        # Accept all permissions for now
        page.setFeaturePermission(
            url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        )

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageFeaturePermissionRequested", page, url, feature
        )

    def _on_certificate_error(self, page, error):
        """Handle certificate error event."""
        # Reject certificate
        error.rejectCertificate()

        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageCertificateError", page, error
        )

    def _on_authentication_required(self, page, url, authenticator):
        """Handle authentication required event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageAuthenticationRequired", page, url, authenticator
        )

    def _on_proxy_authentication_required(self, page, url, authenticator, proxy_host):
        """Handle proxy authentication required event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageProxyAuthenticationRequired", page, url, authenticator, proxy_host
        )

    def _on_render_process_terminated(self, page, status, exit_code):
        """Handle render process terminated event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onPageRenderProcessTerminated", page, status, exit_code
        )

    def create_view(self, profile_name=None):
        """Create a web engine view."""
        try:
            # Create page
            page = self.create_page(profile_name)

            # Create view
            view = QWebEngineView()
            view.setPage(page)

            # Configure view
            self._configure_view(view)

            return view

        except Exception as e:
            self.app_controller.logger.error(f"Error creating view: {e}")
            return None

    def _configure_view(self, view):
        """Configure a web engine view."""
        # Connect signals
        view.loadStarted.connect(lambda: self._on_view_load_started(view))
        view.loadProgress.connect(
            lambda progress: self._on_view_load_progress(view, progress)
        )
        view.loadFinished.connect(
            lambda success: self._on_view_load_finished(view, success)
        )
        view.urlChanged.connect(lambda url: self._on_view_url_changed(view, url))
        view.titleChanged.connect(
            lambda title: self._on_view_title_changed(view, title)
        )
        view.iconChanged.connect(lambda icon: self._on_view_icon_changed(view, icon))

    def _on_view_load_started(self, view):
        """Handle view load started event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onViewLoadStarted", view)

    def _on_view_load_progress(self, view, progress):
        """Handle view load progress event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onViewLoadProgress", view, progress
        )

    def _on_view_load_finished(self, view, success):
        """Handle view load finished event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onViewLoadFinished", view, success
        )

    def _on_view_url_changed(self, view, url):
        """Handle view URL changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onViewUrlChanged", view, url)

    def _on_view_title_changed(self, view, title):
        """Handle view title changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook(
            "onViewTitleChanged", view, title
        )

    def _on_view_icon_changed(self, view, icon):
        """Handle view icon changed event."""
        # Trigger hook
        self.app_controller.hook_registry.trigger_hook("onViewIconChanged", view, icon)
