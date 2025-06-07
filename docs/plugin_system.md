#!/usr/bin/env python3
# NebulaFusion Browser - Plugin System Documentation

# NebulaFusion Browser - Plugin System Documentation

## Overview

The NebulaFusion browser features a robust plugin system that allows developers to extend browser functionality through Python modules. Plugins can interact with all aspects of the browser, from tab management to content manipulation, and can even leverage NebulaFusion's unique features like Reality Augmentation and Dimensional Tabs.

## Plugin Structure

A NebulaFusion plugin consists of at least two files:

1. `__init__.py` - The main plugin code
2. `manifest.json` - Plugin metadata and configuration

These files should be placed in a directory with the plugin's name, which should be placed in the plugins directory (default: `~/.nebulafusion/plugins/`).

Example structure:
```
~/.nebulafusion/plugins/
└── my_plugin/
    ├── __init__.py
    └── manifest.json
```

## Plugin Manifest

The `manifest.json` file defines the plugin's metadata, required permissions, and hooks. Here's an example:

```json
{
    "name": "My Plugin",
    "version": "1.0.0",
    "author": "Developer Name",
    "description": "This plugin adds awesome functionality to NebulaFusion.",
    "min_browser_version": "1.0.0",
    "permissions": [
        "tabs",
        "bookmarks",
        "history",
        "navigation",
        "content",
        "ui"
    ],
    "hooks": [
        "onBrowserStart",
        "onTabCreated",
        "onPageFinishLoad"
    ],
    "default_settings": {
        "enable_feature_x": true,
        "feature_y_color": "#4a86e8"
    }
}
```

### Manifest Fields

- `name`: The display name of the plugin
- `version`: The plugin version (semantic versioning recommended)
- `author`: The plugin author's name
- `description`: A brief description of the plugin
- `min_browser_version`: The minimum NebulaFusion version required
- `permissions`: The browser features the plugin needs access to
- `hooks`: The browser events the plugin wants to handle
- `default_settings`: Default settings for the plugin

## Available Permissions

Plugins must request permissions to access browser features:

| Permission | Description |
|------------|-------------|
| `browser` | Access to browser information and lifecycle |
| `tabs` | Tab creation, manipulation, and access |
| `bookmarks` | Bookmark management |
| `history` | Browsing history access |
| `navigation` | Page navigation control |
| `content` | Page content access and manipulation |
| `ui` | UI customization (toolbars, menus, etc.) |
| `cookies` | Cookie access and management |
| `downloads` | Download management |
| `settings` | Browser settings access |
| `reality_augmentation` | Reality Augmentation feature |
| `collaborative` | Collaborative Browsing feature |
| `content_transform` | Content Transformation feature |
| `time_travel` | Time-Travel Browsing feature |
| `dimensional_tabs` | Dimensional Tabs feature |
| `voice_commands` | Voice Command System |
| `all` | All permissions (use with caution) |

## Available Hooks

Hooks allow plugins to respond to browser events:

### Browser Lifecycle Hooks
- `onBrowserStart`: Called when the browser starts
- `onBrowserExit`: Called when the browser is about to exit
- `onSettingsChanged`: Called when browser settings change

### Tab Hooks
- `onTabCreated`: Called when a new tab is created
- `beforeTabClosed`: Called before a tab is closed
- `onTabClosed`: Called after a tab is closed
- `onTabSelected`: Called when a tab is selected
- `onTabMoved`: Called when a tab is moved

### Navigation Hooks
- `beforeNavigation`: Called before navigating to a URL
- `afterNavigation`: Called after navigating to a URL
- `onPageStartLoad`: Called when a page starts loading
- `onPageLoadProgress`: Called during page load progress
- `onPageFinishLoad`: Called when a page finishes loading
- `onPageError`: Called when a page fails to load

### Content Hooks
- `beforeDOMLoad`: Called before the DOM is loaded
- `afterDOMLoad`: Called after the DOM is loaded
- `onHTMLModify`: Called when HTML is modified
- `onCSSModify`: Called when CSS is modified
- `onJSExecute`: Called when JavaScript is executed

### UI Hooks
- `onToolbarCreated`: Called when the toolbar is created
- `onMenuCreated`: Called when a menu is created
- `onContextMenu`: Called when a context menu is shown
- `onStatusBarUpdate`: Called when the status bar is updated
- `onAddressBarUpdate`: Called when the address bar is updated

### Data Hooks
- `onBookmarkAdded`: Called when a bookmark is added
- `onBookmarkRemoved`: Called when a bookmark is removed
- `onHistoryAdded`: Called when a history entry is added
- `onHistoryRemoved`: Called when a history entry is removed
- `onCookieSet`: Called when a cookie is set
- `onCookieRemoved`: Called when a cookie is removed
- `onCookiesCleared`: Called when cookies are cleared

### Download Hooks
- `onDownloadStart`: Called when a download starts
- `onDownloadProgress`: Called during download progress
- `onDownloadComplete`: Called when a download completes
- `onDownloadError`: Called when a download fails
- `onDownloadCanceled`: Called when a download is canceled

### Unique Feature Hooks
- `onRealityAugmentation`: Called when Reality Augmentation is used
- `onCollaborativeSession`: Called when a Collaborative Session is started
- `onContentTransform`: Called when Content Transformation is used
- `onTimeTravelSnapshot`: Called when a Time-Travel snapshot is taken
- `onDimensionalTabChange`: Called when Dimensional Tabs change
- `onVoiceCommand`: Called when a Voice Command is received

## Plugin Class

The `__init__.py` file should contain a class that implements the plugin functionality. The class must have at least the following methods:

```python
class MyPlugin:
    def __init__(self):
        """Initialize the plugin."""
        self.initialized = False
    
    def initialize(self, api):
        """Initialize the plugin with the provided API."""
        self.api = api
        self.initialized = True
        return True
    
    def shutdown(self):
        """Shutdown the plugin."""
        self.initialized = False
        return True
```

Additionally, the class should implement methods for any hooks specified in the manifest:

```python
def onBrowserStart(self):
    """Handle browser start event."""
    self.api.show_notification("My Plugin", "Browser started!")
    return True

def onTabCreated(self, tab_index):
    """Handle tab created event."""
    tab_info = self.api.get_tab_info(tab_index)
    self.api.show_notification("My Plugin", f"New tab created: {tab_info['title']}")
    return True

def onPageFinishLoad(self, url):
    """Handle page finish load event."""
    self.api.show_notification("My Plugin", f"Page loaded: {url}")
    return True
```

## Plugin API

The plugin API is provided to the plugin during initialization and gives access to browser features. Here's an overview of the available API methods:

### Browser API
- `get_browser_info()`: Get browser information
- `get_version()`: Get browser version
- `restart()`: Restart the browser
- `exit()`: Exit the browser

### Tab API
- `get_tabs()`: Get all tabs
- `get_current_tab()`: Get current tab
- `create_tab(url, background=False, private=False)`: Create new tab
- `close_tab(tab_index)`: Close tab
- `select_tab(tab_index)`: Select tab
- `move_tab(tab_index, new_index)`: Move tab
- `get_tab_info(tab_index)`: Get tab information

### Navigation API
- `navigate(url, new_tab=False)`: Navigate to URL
- `go_back()`: Go back
- `go_forward()`: Go forward
- `reload()`: Reload page
- `stop()`: Stop loading
- `get_current_url()`: Get current URL

### Content API
- `get_page_html()`: Get page HTML
- `get_page_dom()`: Get page DOM
- `inject_css(css)`: Inject CSS
- `inject_js(js)`: Inject JavaScript
- `modify_dom(selector, action)`: Modify DOM elements

### UI API
- `add_toolbar_button(icon, text, callback)`: Add toolbar button
- `add_menu_item(menu, text, callback)`: Add menu item
- `add_context_menu_item(text, callback)`: Add context menu item
- `show_notification(title, message)`: Show notification
- `create_panel(title, content)`: Create side panel

### Data API
- `get_bookmarks()`: Get all bookmarks
- `add_bookmark(url, title, folder="other")`: Add bookmark
- `remove_bookmark(bookmark_id)`: Remove bookmark
- `get_history(limit=100, offset=0, search=None)`: Get browsing history
- `clear_history(time_range=None)`: Clear history
- `get_cookies(domain=None)`: Get cookies
- `set_cookie(cookie)`: Set cookie
- `remove_cookie(name, domain)`: Remove cookie

### Download API
- `download_file(url, path=None)`: Download file
- `pause_download(download_id)`: Pause download
- `resume_download(download_id)`: Resume download
- `cancel_download(download_id)`: Cancel download
- `get_downloads()`: Get all downloads

### Settings API
- `get_settings()`: Get plugin settings
- `set_setting(key, value)`: Set plugin setting
- `get_browser_settings()`: Get browser settings
- `register_settings_page(page)`: Register settings page

### Unique Features API
- `start_reality_augmentation()`: Start reality augmentation
- `start_collaborative_session(session_id=None)`: Start collaborative session
- `transform_content(transform_type)`: Transform content
- `take_time_snapshot()`: Take time travel snapshot
- `organize_dimensional_tabs(arrangement)`: Organize dimensional tabs
- `register_voice_command(command, callback)`: Register voice command

## Plugin Sandboxing

For security, plugins run in a sandboxed environment with the following restrictions:

- Limited CPU usage
- Limited memory usage
- Limited network requests
- Limited file access
- Permission-based API access

Plugins that exceed resource limits or attempt unauthorized actions will be disabled.

## Plugin Settings

Plugins can store and retrieve settings using the Settings API:

```python
# Get plugin settings
settings = self.api.get_settings()

# Get a specific setting with default value
show_notifications = settings.get("show_notifications", True)

# Set a setting
self.api.set_setting("show_notifications", False)
```

Default settings can be specified in the manifest.json file.

## Example Plugin

Here's a simple example plugin that adds a toolbar button and responds to tab creation:

### manifest.json
```json
{
    "name": "Hello World",
    "version": "1.0.0",
    "author": "NebulaFusion Team",
    "description": "A simple hello world plugin for NebulaFusion.",
    "min_browser_version": "1.0.0",
    "permissions": [
        "tabs",
        "ui"
    ],
    "hooks": [
        "onTabCreated"
    ],
    "default_settings": {
        "greeting": "Hello, World!"
    }
}
```

### __init__.py
```python
class HelloWorld:
    def __init__(self):
        self.initialized = False
    
    def initialize(self, api):
        self.api = api
        self.initialized = True
        
        # Get settings
        self.settings = self.api.get_settings()
        
        # Add toolbar button
        self.api.add_toolbar_button(
            "hello_icon.png",
            "Hello",
            self.on_hello_clicked
        )
        
        return True
    
    def shutdown(self):
        self.initialized = False
        return True
    
    def on_hello_clicked(self):
        greeting = self.settings.get("greeting", "Hello, World!")
        self.api.show_notification("Hello World Plugin", greeting)
    
    def onTabCreated(self, tab_index):
        self.api.show_notification(
            "Hello World Plugin",
            "A new tab was created!"
        )
        return True
```

## Best Practices

1. **Request only necessary permissions**: Request only the permissions your plugin actually needs.
2. **Handle errors gracefully**: Check for errors and handle them appropriately.
3. **Clean up resources**: Release resources in the shutdown method.
4. **Respect user settings**: Allow users to configure your plugin's behavior.
5. **Provide clear feedback**: Use notifications to inform users about important actions.
6. **Optimize performance**: Minimize resource usage, especially in frequently called hooks.
7. **Follow UI guidelines**: Maintain consistency with the browser's UI.
8. **Document your plugin**: Provide clear documentation for users.

## Troubleshooting

If your plugin isn't working as expected:

1. Check the browser console for error messages
2. Verify that your plugin has the necessary permissions
3. Ensure your hook methods have the correct signatures
4. Check that your plugin is enabled in the browser settings
5. Verify that your plugin's manifest.json is valid JSON

## Further Resources

- Sample plugins in the `src/plugins/sample_plugins` directory
- NebulaFusion API documentation
- PyQt5 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- Qt WebEngine documentation: https://doc.qt.io/qt-5/qtwebengine-index.html
