#!/usr/bin/env python3
# NebulaFusion Browser - Hook Registry

from PyQt6.QtCore import QObject, pyqtSignal


class HookRegistry(QObject):
    """
    Registry for browser hooks.
    Handles registering, unregistering, and triggering hooks.
    """

    # Signals
    hook_registered = pyqtSignal(str, str)  # hook_name, plugin_id
    hook_unregistered = pyqtSignal(str, str)  # hook_name, plugin_id
    hook_triggered = pyqtSignal(str, list)  # hook_name, args

    def __init__(self, app_controller):
        """Initialize the hook registry."""
        super().__init__()
        self.app_controller = app_controller

        # Hooks
        self._hooks = {}

        # Available hooks
        self.available_hooks = [
            # Browser lifecycle hooks
            "onBrowserStart",
            "onBrowserExit",
            "onProfileCreated",
            # Tab hooks
            "onTabCreated",
            "onTabClosed",
            "onTabSelected",
            "onTabTitleChanged",
            "onTabUrlChanged",
            # Page hooks
            "onPageLoading",
            "onPageLoaded",
            # Navigation hooks
            "onUrlChanged",
            # Download hooks
            "onDownloadStart",
            "onDownloadProgress",
            "onDownloadComplete",
            "onDownloadError",
            "onDownloadCanceled",
            "onDownloadPaused",
            "onDownloadResumed",
            "onDownloadsCleared",
            "onDownloadRemoved",
            # Bookmark hooks
            "onBookmarkAdded",
            "onBookmarkRemoved",
            "onBookmarkUpdated",
            "onBookmarkFolderAdded",
            "onBookmarkFolderRemoved",
            "onBookmarkFolderRenamed",
            "onBookmarksImported",
            "onBookmarksExported",
            # History hooks
            "onHistoryAdded",
            "onHistoryRemoved",
            "onHistoryCleared",
            # Cookie hooks
            "onCookieAdded",
            "onCookieRemoved",
            "onCookiesCleared",
            # Context menu hooks
            "onContextMenu",
            # UI hooks
            "onToolbarCreated",
            "onStatusBarCreated",
            "onAddressBarCreated",
            # Settings hooks
            "onSettingsChanged",
            "onThemeChanged",  # <--- ADD THIS LINE
            # Unique feature hooks
            "onRealityAugmentation",
            "onCollaborativeSession",
            "onContentTransform",
            "onTimeTravelSnapshot",
            "onDimensionalTabChange",
            "onVoiceCommand",
        ]

    # ------------------------------------------------------------------
    # Public API

    @property
    def hooks(self):
        """Return registered hooks."""
        return self._hooks

    def initialize(self):
        """Initialize the hook registry."""
        self.app_controller.logger.info("Initializing hook registry...")

        # Initialize hooks
        for hook_name in self.available_hooks:
            self._hooks[hook_name] = {}

        self.app_controller.logger.info("Hook registry initialized.")

    def register_hook(self, hook_name, plugin_id, callback):
        """Register a hook."""
        # Check if hook exists
        if hook_name not in self.hooks:
            self.app_controller.logger.warning(f"Hook not found: {hook_name}")
            return False

        # Register hook
        self.hooks[hook_name][plugin_id] = callback

        # Emit signal
        self.hook_registered.emit(hook_name, plugin_id)

        self.app_controller.logger.info(f"Hook registered: {hook_name} by {plugin_id}")

        return True

    def unregister_hook(self, hook_name, plugin_id):
        """Unregister a hook."""
        # Check if hook exists
        if hook_name not in self.hooks:
            self.app_controller.logger.warning(f"Hook not found: {hook_name}")
            return False

        # Check if plugin has registered this hook
        if plugin_id not in self.hooks[hook_name]:
            self.app_controller.logger.warning(
                f"Plugin has not registered hook: {hook_name}"
            )
            return False

        # Unregister hook
        del self.hooks[hook_name][plugin_id]

        # Emit signal
        self.hook_unregistered.emit(hook_name, plugin_id)

        self.app_controller.logger.info(
            f"Hook unregistered: {hook_name} by {plugin_id}"
        )

        return True

    def unregister_all_hooks(self, plugin_id):
        """Unregister all hooks for a plugin."""
        # Unregister hooks
        for hook_name in self.hooks:
            if plugin_id in self.hooks[hook_name]:
                self.unregister_hook(hook_name, plugin_id)

    def trigger_hook(self, hook_name, *args, **kwargs):
        if hook_name not in self._hooks:
            self.app_controller.logger.warning(f"Hook not found: {hook_name}")
            return

        self.app_controller.logger.info(f"Triggering hook: {hook_name}")

        for plugin_id, callback in list(self._hooks[hook_name].items()):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                import traceback

                tb = traceback.format_exc()
                self.app_controller.logger.error(
                    f"Error in hook {hook_name} from plugin {plugin_id}: {e}\n{tb}"
                )
                # Disable the faulty plugin
                try:
                    self.app_controller.plugin_manager.disable_plugin(plugin_id)
                    self.app_controller.logger.warning(
                        f"Plugin {plugin_id} disabled due to hook error."
                    )
                except Exception as disable_err:
                    self.app_controller.logger.error(
                        f"Failed to disable plugin {plugin_id}: {disable_err}"
                    )

    def get_registered_hooks(self, plugin_id=None):
        """Get registered hooks."""
        if plugin_id:
            # Get hooks for plugin
            registered_hooks = {}
            for hook_name in self.hooks:
                if plugin_id in self.hooks[hook_name]:
                    registered_hooks[hook_name] = True
            return registered_hooks
        else:
            # Get all registered hooks
            registered_hooks = {}
            for hook_name in self.hooks:
                if self.hooks[hook_name]:
                    registered_hooks[hook_name] = list(self.hooks[hook_name].keys())
            return registered_hooks

    def get_available_hooks(self):
        """Get available hooks."""
        return self.available_hooks
