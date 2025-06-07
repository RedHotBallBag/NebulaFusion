#!/usr/bin/env python3
"""NebulaFusion Browser - Dog House Panel Plugin"""

from __future__ import annotations

from typing import List, Dict
from urllib.parse import quote_plus

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QTextEdit,
    QDockWidget,
)

from src.plugins.plugin_base import PluginBase


class DogHouseWidget(QWidget):
    """Right-hand dock with quick file-extension search helpers."""

    _EXTENSIONS: Dict[str, List[str]] = {
        "Audio": ["mp3", "flac", "wav", "aac", "ogg", "m4a", "wma", "alac"],
        "Video": ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "vob"],
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp"],
        "Documents": [
            "pdf",
            "doc",
            "docx",
            "xls",
            "xlsx",
            "ppt",
            "pptx",
            "odt",
            "epub",
        ],
        "Archives": ["zip", "rar", "7z", "tar", "gz", "bz2", "iso", "dmg"],
        "Code": ["py", "js", "cpp", "cs", "java", "rb", "php", "html", "css"],
        "Misc": ["apk", "cue", "nfo", "srt", "torrent"],
    }

    def __init__(self, api, main_window):
        super().__init__(parent=main_window)
        self.api = api

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)

        poodle_tab = QWidget()
        p_layout = QVBoxLayout(poodle_tab)

        kw_row = QHBoxLayout()
        kw_row.addWidget(QLabel("Keywords:"))
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText('optional words (e.g. "beatles album")')
        kw_row.addWidget(self.keyword_edit, 1)
        p_layout.addLayout(kw_row)

        custom_row = QHBoxLayout()
        custom_row.addWidget(QLabel("Custom ext(s):"))
        self.custom_edit = QLineEdit()
        self.custom_edit.setPlaceholderText("csv | md | psd …")
        custom_row.addWidget(self.custom_edit, 1)
        p_layout.addLayout(custom_row)

        self.checkboxes: List[QCheckBox] = []
        for cat, exts in self._EXTENSIONS.items():
            box = QGroupBox(cat)
            grid = QGridLayout(box)
            for idx, ext in enumerate(exts):
                row, col = divmod(idx, 4)
                cb = QCheckBox(ext)
                self.checkboxes.append(cb)
                grid.addWidget(cb, row, col)
            p_layout.addWidget(box)

        sniff_btn = QPushButton("🐶 Sniff !")
        sniff_btn.clicked.connect(self._sniff)
        p_layout.addWidget(sniff_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        p_layout.addStretch(1)

        self.tabs.addTab(poodle_tab, "Poodle Files")

        for label in ("Gaming", "Mobile"):
            stub = QTextEdit(f"{label} helper coming soon…")
            stub.setReadOnly(True)
            self.tabs.addTab(stub, label)

        self.tabs.currentChanged.connect(self._on_tab_changed)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.tabs)

    # ------------------------------------------------------------------
    def _sniff(self):
        selected = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        custom_raw = self.custom_edit.text().strip()
        if custom_raw:
            selected.extend([p.strip() for p in custom_raw.split("|") if p.strip()])

        if not selected:
            QMessageBox.information(self, "Dog House", "Pick at least one extension.")
            return

        keywords = self.keyword_edit.text().strip()
        parts = ['intitle:"index of"']
        if keywords:
            parts.append(keywords)
        parts.append("(" + " | ".join(selected) + ")")

        query = " ".join(parts)
        url = f"https://www.google.com/search?q={quote_plus(query)}"
        self.api.tabs.new_tab(url)

    def _on_tab_changed(self, index):
        tab_name = self.tabs.tabText(index)
        self.api.logger.info(f"Dog House tab changed: {tab_name}")


class Plugin(PluginBase):
    """Plugin implementation for the Dog House side panel."""

    def __init__(self, api):
        super().__init__(api)
        self.dock: QDockWidget | None = None

    def activate(self):
        try:
            main_window = getattr(self.api.app_controller, "main_window", None)
            if not main_window:
                self.api.logger.error("Main window not available")
                return False

            self._create_dock(main_window)
            self.api.ui.add_toolbar_button(
                button_id="dog_house_toggle",
                text="Dog House",
                tooltip="Toggle Dog House panel",
                callback=self.toggle_panel,
            )
            return True
        except Exception as e:
            self.api.logger.error(f"Failed to activate Dog House plugin: {e}", exc_info=True)
            return False

    def deactivate(self):
        try:
            self.api.ui.remove_toolbar_button("dog_house_toggle")
            if self.dock:
                self.dock.close()
                self.dock.setParent(None)
                self.dock.deleteLater()
                self.dock = None
            return True
        except Exception as e:
            self.api.logger.error(f"Failed to deactivate Dog House plugin: {e}", exc_info=True)
            return False

    # ------------------------------------------------------------------
    def _create_dock(self, main_window):
        if self.dock is None:
            self.dock = QDockWidget("Dog House", main_window)
            self.dock.setObjectName("DogHouseDock")
            widget = DogHouseWidget(self.api, main_window)
            self.dock.setWidget(widget)
            main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
            self.dock.hide()

    def toggle_panel(self):
        if self.dock:
            self.dock.setVisible(not self.dock.isVisible())

