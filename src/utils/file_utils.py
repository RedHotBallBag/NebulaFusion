#!/usr/bin/env python3
# NebulaFusion Browser - File Utilities

import os
import sys
import shutil
import subprocess
import platform
from PyQt6.QtCore import QObject, pyqtSignal

class FileUtils(QObject):
    """
    File utility functions for NebulaFusion browser.
    Provides file operations with platform-specific handling.
    """
    
    # Signals
    file_operation_completed = pyqtSignal(str, bool)  # operation, success
    
    def __init__(self):
        """Initialize the file utilities."""
        super().__init__()
    
    def ensure_directory_exists(self, directory):
        """Ensure that a directory exists, creating it if necessary."""
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                return True
            except Exception as e:
                print(f"Error creating directory {directory}: {e}")
                return False
        return True
    
    def copy_file(self, source, destination):
        """Copy a file from source to destination."""
        try:
            shutil.copy2(source, destination)
            self.file_operation_completed.emit("copy", True)
            return True
        except Exception as e:
            print(f"Error copying file from {source} to {destination}: {e}")
            self.file_operation_completed.emit("copy", False)
            return False
    
    def move_file(self, source, destination):
        """Move a file from source to destination."""
        try:
            shutil.move(source, destination)
            self.file_operation_completed.emit("move", True)
            return True
        except Exception as e:
            print(f"Error moving file from {source} to {destination}: {e}")
            self.file_operation_completed.emit("move", False)
            return False
    
    def delete_file(self, file_path):
        """Delete a file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.file_operation_completed.emit("delete", True)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            self.file_operation_completed.emit("delete", False)
            return False
    
    def read_file(self, file_path, binary=False):
        """Read a file and return its contents."""
        try:
            mode = "rb" if binary else "r"
            with open(file_path, mode) as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, file_path, content, binary=False):
        """Write content to a file."""
        try:
            mode = "wb" if binary else "w"
            with open(file_path, mode) as f:
                f.write(content)
            self.file_operation_completed.emit("write", True)
            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            self.file_operation_completed.emit("write", False)
            return False
    
    def append_to_file(self, file_path, content, binary=False):
        """Append content to a file."""
        try:
            mode = "ab" if binary else "a"
            with open(file_path, mode) as f:
                f.write(content)
            self.file_operation_completed.emit("append", True)
            return True
        except Exception as e:
            print(f"Error appending to file {file_path}: {e}")
            self.file_operation_completed.emit("append", False)
            return False
    
    def file_exists(self, file_path):
        """Check if a file exists."""
        return os.path.isfile(file_path)
    
    def directory_exists(self, directory):
        """Check if a directory exists."""
        return os.path.isdir(directory)
    
    def get_file_size(self, file_path):
        """Get the size of a file in bytes."""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            print(f"Error getting size of file {file_path}: {e}")
            return -1
    
    def get_file_modification_time(self, file_path):
        """Get the modification time of a file."""
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            print(f"Error getting modification time of file {file_path}: {e}")
            return -1
    
    def list_directory(self, directory):
        """List the contents of a directory."""
        try:
            return os.listdir(directory)
        except Exception as e:
            print(f"Error listing directory {directory}: {e}")
            return []
    
    def get_home_directory(self):
        """Get the user's home directory."""
        return os.path.expanduser("~")
    
    def get_downloads_directory(self):
        """Get the user's downloads directory."""
        home = self.get_home_directory()
        
        # Platform-specific downloads directory
        if platform.system() == "Windows":
            return os.path.join(home, "Downloads")
        elif platform.system() == "Darwin":  # macOS
            return os.path.join(home, "Downloads")
        else:  # Linux and others
            # Try to get from XDG user dirs
            try:
                with open(os.path.join(home, ".config", "user-dirs.dirs"), "r") as f:
                    for line in f:
                        if line.startswith("XDG_DOWNLOAD_DIR="):
                            download_dir = line.split("=")[1].strip().strip('"')
                            download_dir = download_dir.replace("$HOME", home)
                            if os.path.exists(download_dir):
                                return download_dir
            except:
                pass
            
            # Fallback to ~/Downloads
            downloads = os.path.join(home, "Downloads")
            if os.path.exists(downloads):
                return downloads
            
            # Last resort: home directory
            return home
    
    def get_temporary_directory(self):
        """Get a temporary directory."""
        import tempfile
        return tempfile.gettempdir()
    
    def create_temporary_file(self, prefix="nebulafusion_", suffix=""):
        """Create a temporary file and return its path."""
        import tempfile
        fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)
        return path
    
    def create_temporary_directory(self, prefix="nebulafusion_"):
        """Create a temporary directory and return its path."""
        import tempfile
        return tempfile.mkdtemp(prefix=prefix)
    
    def open_file(self, file_path):
        """Open a file with the default application."""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", file_path])
            else:  # Linux and others
                subprocess.call(["xdg-open", file_path])
            return True
        except Exception as e:
            print(f"Error opening file {file_path}: {e}")
            return False
    
    def open_folder(self, folder_path):
        """Open a folder in the file explorer."""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", folder_path])
            else:  # Linux and others
                subprocess.call(["xdg-open", folder_path])
            return True
        except Exception as e:
            print(f"Error opening folder {folder_path}: {e}")
            return False
    
    def get_file_extension(self, file_path):
        """Get the extension of a file."""
        return os.path.splitext(file_path)[1]
    
    def get_file_name(self, file_path):
        """Get the name of a file without the path."""
        return os.path.basename(file_path)
    
    def get_file_directory(self, file_path):
        """Get the directory containing a file."""
        return os.path.dirname(file_path)
    
    def join_paths(self, *paths):
        """Join multiple path components."""
        return os.path.join(*paths)
    
    def normalize_path(self, path):
        """Normalize a path (resolve '..' and '.')."""
        return os.path.normpath(path)
    
    def absolute_path(self, path):
        """Convert a path to an absolute path."""
        return os.path.abspath(path)
    
    def relative_path(self, path, start=None):
        """Convert a path to a relative path."""
        return os.path.relpath(path, start)
    
    def is_absolute_path(self, path):
        """Check if a path is absolute."""
        return os.path.isabs(path)
    
    def get_file_mime_type(self, file_path):
        """Get the MIME type of a file."""
        import mimetypes
        mime_type, encoding = mimetypes.guess_type(file_path)
        return mime_type
    
    def extract_zip(self, zip_file, extract_to):
        """Extract a ZIP file to a directory."""
        try:
            import zipfile
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            self.file_operation_completed.emit("extract", True)
            return True
        except Exception as e:
            print(f"Error extracting ZIP file {zip_file}: {e}")
            self.file_operation_completed.emit("extract", False)
            return False
    
    def create_zip(self, zip_file, files_to_zip):
        """Create a ZIP file containing the specified files."""
        try:
            import zipfile
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
                for file in files_to_zip:
                    if os.path.isfile(file):
                        zip_ref.write(file, os.path.basename(file))
                    elif os.path.isdir(file):
                        for root, dirs, files in os.walk(file):
                            for f in files:
                                full_path = os.path.join(root, f)
                                archive_name = os.path.relpath(full_path, os.path.dirname(file))
                                zip_ref.write(full_path, archive_name)
            self.file_operation_completed.emit("zip", True)
            return True
        except Exception as e:
            print(f"Error creating ZIP file {zip_file}: {e}")
            self.file_operation_completed.emit("zip", False)
            return False
