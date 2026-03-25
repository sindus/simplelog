"""
ui.py — SimpleLog Material Design dark UI (PyQt6)
"""

from __future__ import annotations

import json
import os
import re
from collections import deque  # noqa: F401
from dataclasses import dataclass
from datetime import UTC, datetime

from PyQt6.QtCore import (
    QRectF,
    QSize,
    Qt,
    QTimer,  # noqa: F401
    QUrl,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QDesktopServices,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPalette,
    QShortcut,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import i18n

try:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtSvg import QSvgRenderer
    _HAS_SVG = True
except ImportError:
    _HAS_SVG = False

import cloudwatch
from workers import FileWorker, StdinWorker, TailWorker

# ── SVG icon data ──────────────────────────────────────────────────────────────

_SVG_CLOUD = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<path fill="{color}" d="M19.35 10.04A7.49 7.49 0 0 0 12 4'
    'C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14'
    'c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5'
    ' 0-2.64-2.05-4.78-4.65-4.96z"/>'
    "</svg>"
)

_SVG_FOLDER = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
    '<path fill="{color}" d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2'
    'L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2z'
    'm0 12H4V8h16v10z"/>'
    "</svg>"
)


# ── Colour constants ───────────────────────────────────────────────────────────

C_BG        = "#121212"
C_RAIL      = "#0d0d0d"
C_SIDE      = "#1a1a1a"
C_CARD      = "#1e1e1e"
C_TOOLBAR   = "#151515"
C_STATUS    = "#0f0f0f"
C_DIVIDER   = "#2c2c2c"
C_ACCENT    = "#82b1ff"
C_TEXT      = "#e2e2e2"
C_MUTED     = "#6c6c6c"
C_ERR       = "#f28b82"
C_WARN      = "#fdd663"
C_INFO      = "#81c995"
C_DEBUG     = "#82b1ff"
C_TRACE     = "#ce93d8"
C_TS        = "#78d9ec"
C_SEL_BG    = "#1a3a6e"


# ── apply_style ────────────────────────────────────────────────────────────────

def apply_style(app: QApplication) -> None:
    """Apply Material Design dark palette and global stylesheet."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(C_BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.Base,            QColor(C_CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(C_BG))
    palette.setColor(QPalette.ColorRole.Text,            QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.Button,          QColor(C_CARD))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(C_TEXT))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(C_ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(C_MUTED))
    palette.setColor(QPalette.ColorRole.BrightText,      QColor(C_ERR))
    app.setPalette(palette)

    app.setStyleSheet(f"""
        QWidget {{
            background-color: {C_BG};
            color: {C_TEXT};
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background: transparent;
            border: 1px solid #3c3c3c;
            border-radius: 6px;
            padding: 8px 12px;
            color: {C_TEXT};
            min-height: 20px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border-color: {C_ACCENT};
            border-width: 2px;
        }}
        QPushButton {{
            background-color: {C_CARD};
            border: 1px solid #3c3c3c;
            border-radius: 6px;
            padding: 7px 16px;
            color: #c8c8c8;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: #2a2a2a;
            border-color: {C_ACCENT};
        }}
        QPushButton#primary {{
            background-color: {C_ACCENT};
            color: #000000;
            border: none;
            font-weight: bold;
        }}
        QPushButton#primary:hover {{
            background-color: #9dc4ff;
        }}
        QPushButton#danger {{
            color: {C_ERR};
            border-color: {C_ERR};
            background: transparent;
        }}
        QPushButton#danger:hover {{
            background: rgba(242,139,130,0.12);
        }}
        QPushButton:disabled {{
            color: #4c4c4c;
            border-color: {C_DIVIDER};
        }}
        QListWidget {{
            background: #151515;
            border: 1px solid {C_DIVIDER};
            border-radius: 8px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 6px 10px;
            border-radius: 4px;
        }}
        QListWidget::item:selected {{
            background: {C_SEL_BG};
            color: {C_ACCENT};
        }}
        QListWidget::item:hover {{
            background: rgba(255,255,255,0.05);
        }}
        QTabWidget::pane {{
            border: none;
            border-top: 1px solid {C_DIVIDER};
        }}
        QTabBar::tab {{
            background: transparent;
            border: none;
            padding: 10px 18px;
            color: {C_MUTED};
            font-size: 13px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            color: {C_ACCENT};
            border-bottom: 2px solid {C_ACCENT};
        }}
        QTabBar::tab:hover:!selected {{
            color: #c8c8c8;
            background: rgba(255,255,255,0.04);
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background: {C_CARD};
            border: 1px solid #3c3c3c;
            selection-background-color: {C_SEL_BG};
            selection-color: {C_ACCENT};
        }}
        QScrollBar:vertical {{
            background: {C_BG};
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: #3c3c3c;
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {C_ACCENT};
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background: {C_BG};
            height: 8px;
        }}
        QScrollBar::handle:horizontal {{
            background: #3c3c3c;
            border-radius: 4px;
        }}
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        QCheckBox {{
            spacing: 6px;
            color: #a8a8a8;
        }}
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border: 2px solid #4c4c4c;
            border-radius: 3px;
            background: transparent;
        }}
        QCheckBox::indicator:checked {{
            background: {C_ACCENT};
            border-color: {C_ACCENT};
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QToolTip {{
            background: #2a2a2a;
            color: #e2e2e2;
            border: 1px solid #3c3c3c;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }}
        QStatusBar {{
            background: {C_STATUS};
            border-top: 1px solid {C_DIVIDER};
            color: {C_MUTED};
            font-size: 12px;
        }}
        QMenuBar {{
            background: {C_RAIL};
            color: {C_TEXT};
            border-bottom: 1px solid {C_DIVIDER};
            font-size: 13px;
            padding: 2px 4px;
        }}
        QMenuBar::item {{
            background: transparent;
            padding: 5px 12px;
            border-radius: 4px;
        }}
        QMenuBar::item:selected {{
            background: rgba(255,255,255,0.08);
            color: {C_ACCENT};
        }}
        QMenu {{
            background: #1e1e1e;
            border: 1px solid {C_DIVIDER};
            border-radius: 8px;
            padding: 4px 0;
            font-size: 13px;
        }}
        QMenu::item {{
            padding: 8px 24px 8px 16px;
            color: {C_TEXT};
        }}
        QMenu::item:selected {{
            background: {C_SEL_BG};
            color: {C_ACCENT};
        }}
        QMenu::separator {{
            height: 1px;
            background: {C_DIVIDER};
            margin: 4px 8px;
        }}
    """)


# ── NavButton ──────────────────────────────────────────────────────────────────

class NavButton(QAbstractButton):
    """72px-wide nav rail icon button with pill highlight when checked."""

    def __init__(self, svg_template: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(68, 64)
        self.setToolTip(tooltip)
        self._svg_template = svg_template
        self._renderer_checked: QSvgRenderer | None = None
        self._renderer_unchecked: QSvgRenderer | None = None
        if _HAS_SVG:
            self._renderer_checked   = self._make_renderer(C_ACCENT)
            self._renderer_unchecked = self._make_renderer(C_MUTED)

    def _make_renderer(self, color: str) -> QSvgRenderer:
        svg = self._svg_template.replace("{color}", color)
        renderer = QSvgRenderer()
        renderer.load(QByteArray(svg.encode()))
        return renderer

    def paintEvent(self, event):  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        # Pill background when checked
        if self.isChecked():
            pill_w, pill_h = 48, 32
            px = (w - pill_w) // 2
            py = (h - pill_h) // 2
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(C_SEL_BG)))
            path = QPainterPath()
            path.addRoundedRect(px, py, pill_w, pill_h, 16, 16)
            p.drawPath(path)

        # Icon
        icon_size = 22
        ix = (w - icon_size) // 2
        iy = (h - icon_size) // 2
        try:
            if _HAS_SVG:
                renderer = self._renderer_checked if self.isChecked() else self._renderer_unchecked
                if renderer and renderer.isValid():
                    renderer.render(p, QRectF(ix, iy, icon_size, icon_size))
                    return

            # Fallback: draw coloured square placeholder
            color = C_ACCENT if self.isChecked() else C_MUTED
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(color)))
            p.drawRoundedRect(ix, iy, icon_size, icon_size, 4, 4)
        finally:
            p.end()

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(68, 64)


# ── NavRail ────────────────────────────────────────────────────────────────────

class NavRail(QWidget):
    """72px left navigation rail."""

    index_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(72)
        self.setStyleSheet(f"background: {C_RAIL};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 12)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo
        logo = QLabel("SL")
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            f"background: {C_ACCENT}; color: #000; font-weight: bold;"
            "font-size: 15px; border-radius: 12px;"
        )
        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addStretch()
        logo_row.addWidget(logo)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        # Divider
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C_DIVIDER}; border: none;")
        layout.addSpacing(10)
        layout.addWidget(div)
        layout.addSpacing(8)

        # Buttons
        self._buttons: list[NavButton] = []

        self._btn_cw = NavButton(_SVG_CLOUD, "CloudWatch Logs")
        self._btn_file = NavButton(_SVG_FOLDER, "Open log file")

        for btn in (self._btn_cw, self._btn_file):
            btn.clicked.connect(self._on_button_clicked)
            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(0, 0, 0, 0)
            btn_row.addStretch()
            btn_row.addWidget(btn)
            btn_row.addStretch()
            layout.addLayout(btn_row)
            layout.addSpacing(8)
            self._buttons.append(btn)

        layout.addStretch()

        # Select first by default
        self._btn_cw.setChecked(True)

    def _on_button_clicked(self):
        sender = self.sender()
        for i, btn in enumerate(self._buttons):
            btn.setChecked(btn is sender)
        idx = self._buttons.index(sender)
        self.index_changed.emit(idx)


# ── make_card helper ───────────────────────────────────────────────────────────

def make_card(title: str | None = None) -> tuple[QFrame, QVBoxLayout, QLabel | None]:
    """Return (frame, layout, title_label | None) for a Material card."""
    frame = QFrame()
    frame.setStyleSheet(
        f"QFrame {{ background: {C_CARD}; border: 1px solid {C_DIVIDER};"
        f" border-radius: 12px; }}"
    )
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(8)
    title_label: QLabel | None = None
    if title:
        title_label = QLabel(title.upper())
        title_label.setStyleSheet(
            f"color: {C_ACCENT}; font-size: 11px; font-weight: 600;"
            "letter-spacing: 1px; border: none; background: transparent;"
        )
        layout.addWidget(title_label)
    return frame, layout, title_label


# ── Primary button helper ─────────────────────────────────────────────────────

def _primary_btn(text: str = "") -> QPushButton:
    """Create a styled primary (accent-coloured) button.

    Uses an inline stylesheet to ensure the correct appearance even inside
    QScrollArea containers where inherited stylesheets can be unreliable.
    """
    btn = QPushButton(text)
    btn.setObjectName("primary")
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {C_ACCENT};
            color: #000000;
            border: none;
            border-radius: 6px;
            padding: 7px 16px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #9dc4ff;
        }}
        QPushButton:pressed {{
            background-color: #6fa0f0;
        }}
        QPushButton:disabled {{
            background-color: {C_DIVIDER};
            color: #555555;
        }}
    """)
    return btn


# ── Open-mode segmented button widget ─────────────────────────────────────────

class OpenModeWidget(QWidget):
    """Segmented button group: new tab / vertical split / horizontal split."""

    _MODES = ("tab", "vertical", "horizontal")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 4, 0, 0)
        vbox.setSpacing(6)

        self._lbl = QLabel()
        self._lbl.setStyleSheet(
            f"color: {C_MUTED}; font-size: 11px; font-weight: 600;"
            " letter-spacing: 1px; background: transparent; border: none;"
        )
        vbox.addWidget(self._lbl)

        # Segmented button container
        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ background: {C_CARD}; border: 1px solid {C_DIVIDER};"
            f" border-radius: 8px; }}"
        )
        seg_layout = QVBoxLayout(seg)
        seg_layout.setContentsMargins(3, 3, 3, 3)
        seg_layout.setSpacing(2)

        self._grp = QButtonGroup(self)
        self._btns: dict[str, QPushButton] = {}
        n = len(self._MODES)
        for idx, mode in enumerate(self._MODES):
            btn = QPushButton()
            btn.setCheckable(True)
            # Per-position border-radius so the group looks connected
            if idx == 0:
                r = "border-radius: 5px 5px 3px 3px;"
            elif idx == n - 1:
                r = "border-radius: 3px 3px 5px 5px;"
            else:
                r = "border-radius: 3px;"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {C_MUTED};
                    font-size: 12px;
                    padding: 7px 10px;
                    text-align: left;
                    {r}
                }}
                QPushButton:checked {{
                    background: {C_SEL_BG};
                    color: {C_ACCENT};
                    font-weight: 600;
                }}
                QPushButton:hover:!checked {{
                    background: rgba(255,255,255,0.05);
                    color: {C_TEXT};
                }}
            """)
            self._grp.addButton(btn, idx)
            seg_layout.addWidget(btn)
            self._btns[mode] = btn

        self._btns["tab"].setChecked(True)
        vbox.addWidget(seg)

        _key = id(self)
        i18n.register(_key, self.retranslate)
        self.destroyed.connect(lambda _=None, k=_key: i18n.unregister(k))
        self.retranslate()

    def get_mode(self) -> str:
        for mode, btn in self._btns.items():
            if btn.isChecked():
                return mode
        return "tab"

    def retranslate(self) -> None:
        self._lbl.setText(i18n.tr("open_as").upper())
        self._btns["tab"].setText(i18n.tr("open_mode_tab"))
        self._btns["vertical"].setText(i18n.tr("open_mode_vertical"))
        self._btns["horizontal"].setText(i18n.tr("open_mode_horizontal"))


# ── CloudWatchPanel ────────────────────────────────────────────────────────────

class CloudWatchPanel(QWidget):
    open_tab = pyqtSignal(dict, str)  # (cfg, split_mode)

    _REGIONS = [
        "us-east-1", "us-east-2", "us-west-1", "us-west-2",
        "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
        "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
        "ap-south-1", "ca-central-1", "sa-east-1",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._client = None
        self._all_groups: list[str] = []
        self._build_ui()
        _key = id(self)
        i18n.register(_key, self.retranslate)
        self.destroyed.connect(lambda _=None, k=_key: i18n.unregister(k))

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setFixedWidth(268)
        content.setStyleSheet(f"background: {C_SIDE};")

        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(12, 16, 12, 16)
        vbox.setSpacing(12)

        # Title
        self._title_lbl = QLabel()
        self._title_lbl.setStyleSheet(
            f"color: {C_TEXT}; font-size: 18px; font-weight: bold;"
            "background: transparent; border: none;"
        )
        vbox.addWidget(self._title_lbl)

        # ── CONNECTION card ──
        card, cl, self._lbl_connection = make_card(i18n.tr("cw_card_connection"))
        profiles = cloudwatch.list_profiles()
        self.profile_combo = QComboBox()
        self.profile_combo.addItem("(default)")
        self.profile_combo.addItems(list(profiles))

        self.region_combo = QComboBox()
        self.region_combo.setEditable(True)
        self.region_combo.addItems(self._REGIONS)

        self.connect_btn = _primary_btn()
        self.connect_btn.clicked.connect(self._on_connect)

        self._lbl_profile = _field_label("")
        self._lbl_region  = _field_label("")
        cl.addWidget(self._lbl_profile)
        cl.addWidget(self.profile_combo)
        cl.addWidget(self._lbl_region)
        cl.addWidget(self.region_combo)
        cl.addWidget(self.connect_btn)
        vbox.addWidget(card)

        # ── LOG GROUPS card ──
        card2, gl, self._lbl_groups = make_card(i18n.tr("cw_card_groups"))
        self.group_search = QLineEdit()
        self.group_search.textChanged.connect(self._filter_groups)
        self.group_list = QListWidget()
        self.group_list.setMaximumHeight(180)
        self.group_list.currentTextChanged.connect(self._on_group_selected)

        gl.addWidget(self.group_search)
        gl.addWidget(self.group_list)
        vbox.addWidget(card2)

        # ── LOG STREAMS card ──
        card3, sl, self._lbl_streams = make_card(i18n.tr("cw_card_streams"))
        self.stream_list = QListWidget()
        self.stream_list.setMaximumHeight(150)

        sl.addWidget(self.stream_list)
        vbox.addWidget(card3)

        # ── OPTIONS card ──
        card4, ol, self._lbl_options = make_card(i18n.tr("cw_card_options"))

        self.lookback_combo = QComboBox()
        for label, secs in [
            ("15 min", 900), ("1 hour", 3600), ("6 hours", 21600),
            ("24 hours", 86400), ("3 days", 259200), ("7 days", 604800),
        ]:
            self.lookback_combo.addItem(label, secs)
        self.lookback_combo.setCurrentIndex(1)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(3)
        self.interval_spin.setSuffix(" s")

        self.filter_input = QLineEdit()

        self._open_mode_w = OpenModeWidget()
        self._get_open_mode = self._open_mode_w.get_mode

        self.open_btn = _primary_btn()
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._on_open_clicked)

        self._lbl_lookback = _field_label("")
        self._lbl_poll     = _field_label("")
        self._lbl_filter   = _field_label("")
        ol.addWidget(self._lbl_lookback)
        ol.addWidget(self.lookback_combo)
        ol.addWidget(self._lbl_poll)
        ol.addWidget(self.interval_spin)
        ol.addWidget(self._lbl_filter)
        ol.addWidget(self.filter_input)
        ol.addWidget(self._open_mode_w)
        ol.addWidget(self.open_btn)
        vbox.addWidget(card4)

        vbox.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.retranslate()

    def retranslate(self) -> None:
        self._title_lbl.setText(i18n.tr("cw_title"))
        if self._lbl_connection:
            self._lbl_connection.setText(i18n.tr("cw_card_connection").upper())
        if self._lbl_groups:
            self._lbl_groups.setText(i18n.tr("cw_card_groups").upper())
        if self._lbl_streams:
            self._lbl_streams.setText(i18n.tr("cw_card_streams").upper())
        if self._lbl_options:
            self._lbl_options.setText(i18n.tr("cw_card_options").upper())
        self._lbl_profile.setText(i18n.tr("cw_field_profile"))
        self._lbl_region.setText(i18n.tr("cw_field_region"))
        self._lbl_lookback.setText(i18n.tr("cw_field_lookback"))
        self._lbl_poll.setText(i18n.tr("cw_field_poll"))
        self._lbl_filter.setText(i18n.tr("cw_field_filter"))
        self.group_search.setPlaceholderText(i18n.tr("cw_search_groups"))
        self.filter_input.setPlaceholderText(i18n.tr("cw_filter_ph"))
        self.open_btn.setText(i18n.tr("cw_open"))
        # connect_btn: derive label from connection state, not from current text
        if not getattr(self, "_connecting", False):
            self.connect_btn.setText(
                i18n.tr("cw_refresh") if self._client else i18n.tr("cw_connect")
            )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _on_connect(self):
        profile = self.profile_combo.currentText()
        region  = self.region_combo.currentText()
        self._connecting = True
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText(i18n.tr("cw_connecting"))
        try:
            self._client = cloudwatch.make_client(
                None if profile == "(default)" else profile, region
            )
            groups = cloudwatch.list_log_groups(self._client)
            self._all_groups = groups
            self._populate_groups(groups)
            self.connect_btn.setText(i18n.tr("cw_refresh"))
        except Exception as exc:
            QMessageBox.critical(self, i18n.tr("err_connection"), str(exc))
            self.connect_btn.setText(i18n.tr("cw_connect"))
        finally:
            self._connecting = False
            self.connect_btn.setEnabled(True)

    def _populate_groups(self, groups: list[str]):
        self.group_list.clear()
        for g in groups:
            self.group_list.addItem(g)

    def _filter_groups(self, text: str):
        lo = text.lower()
        self._populate_groups([g for g in self._all_groups if lo in g.lower()])

    def _on_group_selected(self, group: str):
        if not group or not self._client:
            return
        self.stream_list.clear()
        try:
            streams = cloudwatch.list_log_streams(self._client, group)
            all_item = QListWidgetItem("— All streams —")
            all_item.setForeground(QColor(C_ACCENT))
            self.stream_list.addItem(all_item)
            for s in streams:
                self.stream_list.addItem(s)
            self.stream_list.setCurrentRow(0)
        except Exception as exc:
            QMessageBox.warning(self, i18n.tr("err_streams"), str(exc))
        self.open_btn.setEnabled(True)

    def _on_open_clicked(self):
        group_item  = self.group_list.currentItem()
        stream_item = self.stream_list.currentItem()
        if not self._client or not group_item:
            return
        stream_name = ""
        if stream_item and stream_item.text() != "— All streams —":
            stream_name = stream_item.text()
        self.open_tab.emit({
            "type":     "cloudwatch",
            "client":   self._client,
            "group":    group_item.text(),
            "stream":   stream_name,
            "filter":   self.filter_input.text(),
            "interval": self.interval_spin.value(),
            "lookback": self.lookback_combo.currentData(),
        }, self._get_open_mode())


# ── FilePanel ──────────────────────────────────────────────────────────────────

class FilePanel(QWidget):
    open_tab = pyqtSignal(str, int, str)  # (path, tail_lines, split_mode)

    _MAX_RECENT = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._recent: list[str] = []
        self._build_ui()
        _key = id(self)
        i18n.register(_key, self.retranslate)
        self.destroyed.connect(lambda _=None, k=_key: i18n.unregister(k))

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(12, 16, 12, 16)
        vbox.setSpacing(12)
        self.setFixedWidth(268)
        self.setStyleSheet(f"background: {C_SIDE};")

        self._title_lbl = QLabel()
        self._title_lbl.setStyleSheet(
            f"color: {C_TEXT}; font-size: 18px; font-weight: bold;"
            "background: transparent; border: none;"
        )
        vbox.addWidget(self._title_lbl)

        # ── OPEN FILE card ──
        card, cl, self._lbl_card_open = make_card(i18n.tr("file_card_open"))
        self._desc_lbl = QLabel()
        self._desc_lbl.setWordWrap(True)
        self._desc_lbl.setStyleSheet(
            f"color: {C_MUTED}; font-size: 12px; background: transparent; border: none;"
        )

        # Tail lines selector
        tail_row = QHBoxLayout()
        tail_row.setSpacing(8)
        self._tail_lbl = QLabel()
        self._tail_lbl.setStyleSheet(
            f"color: {C_MUTED}; font-size: 12px; background: transparent; border: none;"
        )
        self._tail_spin = QSpinBox()
        self._tail_spin.setRange(1, 500_000)
        self._tail_spin.setValue(100)
        self._tail_spin.setSingleStep(100)
        tail_row.addWidget(self._tail_lbl)
        tail_row.addWidget(self._tail_spin)
        tail_row.addStretch()

        self._open_mode_w = OpenModeWidget()
        self._get_open_mode = self._open_mode_w.get_mode

        self._browse_btn = _primary_btn()
        self._browse_btn.clicked.connect(self._on_browse)

        cl.addWidget(self._desc_lbl)
        cl.addLayout(tail_row)
        cl.addWidget(self._open_mode_w)
        cl.addWidget(self._browse_btn)
        vbox.addWidget(card)

        # ── RECENT FILES card ──
        card2, rl, self._lbl_card_recent = make_card(i18n.tr("file_card_recent"))
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(220)
        self.recent_list.itemDoubleClicked.connect(self._on_recent_double_click)

        self.empty_label = QLabel()
        self.empty_label.setStyleSheet(
            "color: #4c4c4c; font-size: 12px; background: transparent; border: none;"
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        rl.addWidget(self.recent_list)
        rl.addWidget(self.empty_label)
        vbox.addWidget(card2)

        vbox.addStretch()
        self.retranslate()
        self._refresh_recent_ui()

    def retranslate(self) -> None:
        self._title_lbl.setText(i18n.tr("file_title"))
        if self._lbl_card_open:
            self._lbl_card_open.setText(i18n.tr("file_card_open").upper())
        if self._lbl_card_recent:
            self._lbl_card_recent.setText(i18n.tr("file_card_recent").upper())
        self._desc_lbl.setText(i18n.tr("file_desc"))
        self._tail_lbl.setText(i18n.tr("file_last_lines"))
        self._browse_btn.setText(i18n.tr("file_browse"))
        self.empty_label.setText(i18n.tr("file_no_recent"))

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open log file",
            os.path.expanduser("~"),
            "Log files (*.log *.txt *.out *.err *.json);;All files (*)",
        )
        if path:
            self._open_path(path)

    def _on_recent_double_click(self, item: QListWidgetItem):
        path = item.toolTip()
        if os.path.isfile(path):
            self._open_path(path)
        else:
            QMessageBox.warning(
                self,
                i18n.tr("err_file_not_found"),
                i18n.tr("err_cannot_open", path=path),
            )

    def _open_path(self, path: str):
        if path in self._recent:
            self._recent.remove(path)
        self._recent.insert(0, path)
        self._recent = self._recent[: self._MAX_RECENT]
        self._refresh_recent_ui()
        self.open_tab.emit(path, self._tail_spin.value(), self._get_open_mode())

    def _refresh_recent_ui(self):
        self.recent_list.clear()
        if self._recent:
            self.recent_list.show()
            self.empty_label.hide()
            for p in self._recent:
                item = QListWidgetItem(os.path.basename(p))
                item.setToolTip(p)
                self.recent_list.addItem(item)
        else:
            self.recent_list.hide()
            self.empty_label.show()


# ── SideStack ─────────────────────────────────────────────────────────────────

class SideStack(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(268)
        self.setStyleSheet(
            f"background: {C_SIDE};"
            f"border-right: 1px solid {C_DIVIDER};"
        )


# ── Filter / search data model ─────────────────────────────────────────────────

@dataclass
class TermRow:
    text: str
    operator: str  # "AND" | "OR" | "" — empty string for the first term (ignored)


def _line_matches(line: str, terms: list[TermRow]) -> bool:
    """Return True if *line* satisfies the AND/OR chain of *terms* (case-insensitive)."""
    if not terms:
        return True
    low = line.lower()
    result = terms[0].text.lower() in low
    for term in terms[1:]:
        hit = term.text.lower() in low
        result = (result and hit) if term.operator == "AND" else (result or hit)
    return result


def _extract_json_keys(line: str) -> set[str]:
    """Extract top-level JSON keys from *line*. Best-effort; never raises."""
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            return set(obj.keys())
    except (json.JSONDecodeError, ValueError):
        pass
    # Fallback: regex for "key": patterns (handles JSON embedded in a longer line)
    return set(re.findall(r'"([\w_-]+)"\s*:', line))


# ── LogHighlighter ─────────────────────────────────────────────────────────────

class LogHighlighter(QSyntaxHighlighter):
    RULES = [
        (re.compile(r"\b(CRITICAL|FATAL)\b",  re.IGNORECASE), C_ERR,   True),
        (re.compile(r"\b(ERROR|ERR)\b",        re.IGNORECASE), C_ERR,   False),
        (re.compile(r"\b(WARN(?:ING)?)\b",     re.IGNORECASE), C_WARN,  False),
        (re.compile(r"\b(INFO)\b",             re.IGNORECASE), C_INFO,  False),
        (re.compile(r"\b(DEBUG)\b",            re.IGNORECASE), C_DEBUG, False),
        (re.compile(r"\b(TRACE)\b",            re.IGNORECASE), C_TRACE, False),
        (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"), C_TS,  False),
        (re.compile(r'"[\w_-]+"(?=\s*:)'),     C_TRACE, False),
    ]

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        for pattern, color, bold in self.RULES:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(700)
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ── LogViewer ─────────────────────────────────────────────────────────────────

_SOURCE_COLORS = {
    "cloudwatch": C_ACCENT,
    "file":       C_INFO,
    "stdin":      C_WARN,
}


class _LogTextEdit(QTextEdit):
    """QTextEdit that emits enter_pressed on Return/Enter key."""
    enter_pressed = pyqtSignal()

    def keyPressEvent(self, event):  # noqa: N802
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enter_pressed.emit()
        else:
            super().keyPressEvent(event)


class LogViewer(QWidget):
    stop_requested = pyqtSignal()

    _MAX_LINES = 10_000

    def __init__(self, source_type: str = "cloudwatch", parent=None):
        super().__init__(parent)
        self._source_type = source_type
        self._line_count  = 0
        self._build_ui()
        _key = id(self)
        i18n.register(_key, self.retranslate)
        self.destroyed.connect(lambda _=None, k=_key: i18n.unregister(k))

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Toolbar ──
        toolbar = QWidget()
        toolbar.setFixedHeight(48)
        toolbar.setStyleSheet(
            f"background: {C_TOOLBAR}; border-bottom: 1px solid {C_DIVIDER};"
        )
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(12, 0, 12, 0)
        tb.setSpacing(8)

        # Source badge
        src_color = _SOURCE_COLORS.get(self._source_type, C_TEXT)
        self._source_badge = QLabel(self._source_type.upper())
        self._source_badge.setStyleSheet(
            f"background: {C_SEL_BG}; color: {src_color}; border-radius: 10px;"
            "padding: 2px 10px; font-size: 11px; font-weight: bold; border: none;"
        )

        self.title_label = QLabel("—")
        self.title_label.setStyleSheet(
            f"font-weight: bold; color: {C_TEXT}; background: transparent; border: none;"
        )

        self.line_badge = QLabel(i18n.tr("viewer_lines", n=0))
        self.line_badge.setStyleSheet(
            f"background: {C_CARD}; color: {C_MUTED}; border-radius: 10px;"
            "padding: 2px 10px; font-size: 11px; border: none;"
        )

        self.search_input = QLineEdit()
        self.search_input.setMaximumWidth(220)
        self.search_input.returnPressed.connect(self._search_next)

        self.autoscroll_cb = QCheckBox()
        self.autoscroll_cb.setChecked(True)

        self.timestamps_cb = QCheckBox()
        self.timestamps_cb.setChecked(True)

        self.clear_btn = QPushButton()
        self.clear_btn.setObjectName("danger")
        self.clear_btn.setFixedHeight(32)
        self.clear_btn.clicked.connect(self.clear)

        self.stop_btn = QPushButton()
        self.stop_btn.setFixedHeight(32)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_requested)

        tb.addWidget(self._source_badge)
        tb.addWidget(self.title_label)
        tb.addStretch()
        tb.addWidget(self.line_badge)
        tb.addWidget(self.search_input)
        tb.addWidget(self.autoscroll_cb)
        tb.addWidget(self.timestamps_cb)
        tb.addWidget(self.clear_btn)
        tb.addWidget(self.stop_btn)
        layout.addWidget(toolbar)

        # ── Text area ──
        self.text_edit = _LogTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet(
            f"background: {C_RAIL}; border: none; border-radius: 0;"
            "font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;"
            "font-size: 12px; color: #d4d4d4;"
        )
        self.text_edit.enter_pressed.connect(self._insert_separator)
        self._highlighter = LogHighlighter(self.text_edit.document())
        layout.addWidget(self.text_edit)

        # Ctrl+F shortcut
        sc = QShortcut(QKeySequence("Ctrl+F"), self)
        sc.activated.connect(lambda: self.search_input.setFocus())

        self.retranslate()

    def retranslate(self) -> None:
        src_key = f"src_{self._source_type}"
        self._source_badge.setText(i18n.tr(src_key))
        self.autoscroll_cb.setText(i18n.tr("viewer_autoscroll"))
        self.timestamps_cb.setText(i18n.tr("viewer_timestamps"))
        self.clear_btn.setText(i18n.tr("viewer_clear"))
        self.stop_btn.setText(i18n.tr("viewer_stop"))
        self.search_input.setPlaceholderText(i18n.tr("viewer_search_ph"))
        self.line_badge.setText(i18n.tr("viewer_lines", n=self._line_count))

    # ── Public API ────────────────────────────────────────────────────────────

    def set_title(self, text: str):
        self.title_label.setText(text)

    def append_events(self, events: list[tuple[int, str]]):
        cursor = self.text_edit.textCursor()
        show_ts = self.timestamps_cb.isChecked()

        for ts_ms, message in events:
            # Trim oldest line if over limit
            if self._line_count >= self._MAX_LINES:
                c2 = self.text_edit.textCursor()
                c2.movePosition(QTextCursor.MoveOperation.Start)
                c2.movePosition(
                    QTextCursor.MoveOperation.Down,
                    QTextCursor.MoveMode.KeepAnchor,
                )
                c2.removeSelectedText()
                self._line_count -= 1

            cursor.movePosition(QTextCursor.MoveOperation.End)
            if show_ts and ts_ms:
                ts_str = datetime.fromtimestamp(
                    ts_ms / 1000, tz=UTC
                ).strftime("%H:%M:%S")
                line = f"[{ts_str}]  {message}"
            else:
                line = message

            default_fmt = QTextCharFormat()
            default_fmt.setForeground(QColor("#d4d4d4"))
            if self._line_count > 0:
                cursor.insertText("\n", default_fmt)
            cursor.insertText(line, default_fmt)
            self._line_count += 1

        self.line_badge.setText(i18n.tr("viewer_lines", n=self._line_count))
        if self.autoscroll_cb.isChecked():
            sb = self.text_edit.verticalScrollBar()
            sb.setValue(sb.maximum())

    def clear(self):
        self.text_edit.clear()
        self._line_count = 0
        self.line_badge.setText(i18n.tr("viewer_lines", n=0))

    def _insert_separator(self):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        sep = f"─── {ts} " + "─" * 52
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if self._line_count > 0:
            cursor.insertText("\n")
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#4a6080"))
        cursor.insertText(sep, fmt)
        cursor.setCharFormat(QTextCharFormat())  # reset to default
        self._line_count += 1
        self.line_badge.setText(i18n.tr("viewer_lines", n=self._line_count))
        sb = self.text_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _search_next(self):
        text = self.search_input.text()
        if not text:
            return
        if not self.text_edit.find(text):
            c = self.text_edit.textCursor()
            c.movePosition(QTextCursor.MoveOperation.Start)
            self.text_edit.setTextCursor(c)
            self.text_edit.find(text)


# ── MainWindow ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleLog")
        self.resize(1380, 860)
        self._workers: dict[int, object] = {}
        self._panes: list[QTabWidget] = []
        self._active_pane: QTabWidget | None = None
        self._update_worker = None  # UpdateWorker instance (kept alive)
        self._build_ui()
        self._build_menubar()

    def _build_ui(self):
        # Central container
        central = QWidget()
        central.setStyleSheet(f"background: {C_BG};")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Nav rail
        self._nav = NavRail()
        self._nav.index_changed.connect(self._on_nav_index_changed)
        root.addWidget(self._nav)

        # Side stack
        self._side_stack = SideStack()

        self._cw_panel = CloudWatchPanel()
        self._cw_panel.open_tab.connect(self.open_cloudwatch_tab)
        self._side_stack.addWidget(self._cw_panel)

        self._file_panel = FilePanel()
        self._file_panel.open_tab.connect(self.open_file_tab)
        self._side_stack.addWidget(self._file_panel)

        root.addWidget(self._side_stack)

        # Splitter (hosts one or two tab-panes)
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {C_DIVIDER}; }}"
            f"QSplitter::handle:horizontal {{ width: 5px; }}"
            f"QSplitter::handle:vertical {{ height: 5px; }}"
            f"QSplitter::handle:hover {{ background: {C_ACCENT}; }}"
        )
        first_pane = self._make_pane()
        self._splitter.addWidget(first_pane)
        self._panes.append(first_pane)
        self._active_pane = first_pane
        root.addWidget(self._splitter, stretch=1)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage(i18n.tr("status_ready"))

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menubar(self) -> None:
        mb = self.menuBar()

        # ── File ──
        self._menu_file = mb.addMenu("")
        self._act_open = QAction(self)
        self._act_open.setShortcut(QKeySequence("Ctrl+O"))
        self._act_open.triggered.connect(self._action_open_file)
        self._menu_file.addAction(self._act_open)

        self._act_update = QAction(self)
        self._act_update.triggered.connect(self._action_check_update)
        self._menu_file.addAction(self._act_update)

        self._menu_file.addSeparator()

        self._act_quit = QAction(self)
        self._act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        self._act_quit.triggered.connect(self.close)
        self._menu_file.addAction(self._act_quit)

        # ── Edit ──
        self._menu_edit = mb.addMenu("")
        self._act_copy = QAction(self)
        self._act_copy.setShortcut(QKeySequence("Ctrl+C"))
        self._act_copy.triggered.connect(self._action_copy)
        self._menu_edit.addAction(self._act_copy)

        self._act_paste = QAction(self)
        self._act_paste.setShortcut(QKeySequence("Ctrl+V"))
        self._act_paste.triggered.connect(self._action_paste)
        self._menu_edit.addAction(self._act_paste)

        self._menu_edit.addSeparator()

        self._act_break = QAction(self)
        self._act_break.setShortcut(QKeySequence("Ctrl+Return"))
        self._act_break.triggered.connect(self._action_break)
        self._menu_edit.addAction(self._act_break)

        # ── Language ──
        self._menu_lang = mb.addMenu("")
        ag = QButtonGroup(self)  # not actually needed but keeps logic tidy
        ag  # noqa: B018

        self._act_lang_en = QAction(self)
        self._act_lang_en.setCheckable(True)
        self._act_lang_en.triggered.connect(lambda: self._action_set_language("en"))
        self._menu_lang.addAction(self._act_lang_en)

        self._act_lang_fr = QAction(self)
        self._act_lang_fr.setCheckable(True)
        self._act_lang_fr.triggered.connect(lambda: self._action_set_language("fr"))
        self._menu_lang.addAction(self._act_lang_fr)

        # ── Help ──
        self._menu_help = mb.addMenu("")
        self._act_help_ref = QAction(self)
        self._act_help_ref.triggered.connect(self._action_help)
        self._menu_help.addAction(self._act_help_ref)

        self._retranslate_menubar()

    def _retranslate_menubar(self) -> None:
        locale = i18n.get_locale()
        self._menu_file.setTitle(i18n.tr("menu_file"))
        self._act_open.setText(i18n.tr("action_open"))
        self._act_update.setText(i18n.tr("action_update"))
        self._act_quit.setText(i18n.tr("action_quit"))
        self._menu_edit.setTitle(i18n.tr("menu_edit"))
        self._act_copy.setText(i18n.tr("action_copy"))
        self._act_paste.setText(i18n.tr("action_paste"))
        self._act_break.setText(i18n.tr("action_break"))
        self._menu_lang.setTitle(i18n.tr("menu_language"))
        self._act_lang_en.setText(i18n.tr("lang_english"))
        self._act_lang_en.setChecked(locale == "en")
        self._act_lang_fr.setText(i18n.tr("lang_french"))
        self._act_lang_fr.setChecked(locale == "fr")
        self._menu_help.setTitle(i18n.tr("menu_help"))
        self._act_help_ref.setText(i18n.tr("action_help_ref"))

    # ── Menu action handlers ───────────────────────────────────────────────────

    def _action_open_file(self) -> None:
        """File → Open: browse and open a log file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            i18n.tr("action_open"),
            os.path.expanduser("~"),
            "Log files (*.log *.txt *.out *.err *.json);;All files (*)",
        )
        if path and os.path.isfile(path):
            self.open_file_tab(path)
            # Also update FilePanel's recent list
            self._file_panel._open_path(path)

    def _action_check_update(self) -> None:
        """File → Check for Updates: async GitHub release check."""
        from version import __version__
        from workers import UpdateWorker

        self._update_worker = UpdateWorker(__version__)
        self._update_worker.up_to_date.connect(self._on_up_to_date)
        self._update_worker.update_available.connect(self._on_update_available)
        self._update_worker.error.connect(
            lambda msg: QMessageBox.warning(
                self, i18n.tr("update_title"), i18n.tr("update_error", error=msg)
            )
        )
        self._act_update.setEnabled(False)
        self._update_worker.finished.connect(lambda: self._act_update.setEnabled(True))
        self._update_worker.start()

    def _on_up_to_date(self, version: str) -> None:
        QMessageBox.information(
            self,
            i18n.tr("update_title"),
            i18n.tr("update_up_to_date", version=version),
        )

    def _on_update_available(self, latest: str, url: str) -> None:
        from version import __version__
        box = QMessageBox(self)
        box.setWindowTitle(i18n.tr("update_title"))
        box.setText(i18n.tr("update_available", latest=latest, current=__version__))
        download_btn = box.addButton(i18n.tr("update_download"), QMessageBox.ButtonRole.AcceptRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()
        if box.clickedButton() is download_btn:
            QDesktopServices.openUrl(QUrl(url))

    def _action_copy(self) -> None:
        """Edit → Copy: copy selected text from active viewer."""
        viewer = self._active_viewer()
        if viewer:
            viewer.text_edit.copy()

    def _action_paste(self) -> None:
        """Edit → Paste: paste clipboard text into active viewer's search bar."""
        viewer = self._active_viewer()
        if viewer:
            viewer.search_input.setFocus()
            viewer.search_input.paste()

    def _action_break(self) -> None:
        """Edit → Break: insert a visual separator in the active viewer."""
        viewer = self._active_viewer()
        if viewer:
            viewer._insert_separator()

    def _action_help(self) -> None:
        """Help → CLI Reference: show documentation dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle(i18n.tr("help_title"))
        dlg.resize(560, 480)
        dlg.setStyleSheet(f"background: {C_BG}; color: {C_TEXT};")

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(i18n.tr("help_content"))
        text.setStyleSheet(
            f"background: {C_CARD}; border: 1px solid {C_DIVIDER}; border-radius: 8px;"
            "font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 13px;"
            f"color: {C_TEXT}; padding: 12px;"
        )
        layout.addWidget(text)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(dlg.accept)
        btns.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(btns)

        dlg.exec()

    def _action_set_language(self, locale: str) -> None:
        i18n.set_locale(locale)
        i18n.retranslate_all()
        self._retranslate_menubar()
        self._status.showMessage(i18n.tr("status_ready"))

    def _active_viewer(self) -> LogViewer | None:
        """Return the LogViewer in the currently active tab, or None."""
        if not self._active_pane:
            return None
        widget = self._active_pane.currentWidget()
        return widget if isinstance(widget, LogViewer) else None

    # ── Pane management ───────────────────────────────────────────────────────

    def _make_pane(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        tabs.setDocumentMode(True)
        tabs.setStyleSheet(f"background: {C_BG};")
        tabs.setMinimumWidth(50)
        tabs.setMinimumHeight(50)
        tabs.tabCloseRequested.connect(lambda idx, t=tabs: self._close_tab(idx, t))
        # Clicking any tab in a pane makes it the active pane
        tabs.currentChanged.connect(lambda _, t=tabs: self._set_active_pane(t))
        return tabs

    def _set_active_pane(self, pane: QTabWidget):
        self._active_pane = pane

    _MAX_PANES = 9

    def _make_sub_splitter(self, orientation: Qt.Orientation) -> QSplitter:
        s = QSplitter(orientation)
        s.setChildrenCollapsible(False)
        s.setStyleSheet(self._splitter.styleSheet())
        return s

    def _get_or_create_secondary_pane(self, orientation: Qt.Orientation) -> QTabWidget:
        if len(self._panes) >= self._MAX_PANES:
            return self._panes[-1]

        new_pane = self._make_pane()
        self._panes.append(new_pane)
        active = self._active_pane

        # Find the direct parent splitter of the active pane
        parent_spl = active.parent()

        if isinstance(parent_spl, QSplitter) and parent_spl.orientation() == orientation:
            # Same orientation: insert the new pane right after the active one
            idx = parent_spl.indexOf(active)
            parent_spl.insertWidget(idx + 1, new_pane)
            n = parent_spl.count()
            dim = (parent_spl.width() if orientation == Qt.Orientation.Horizontal
                   else parent_spl.height())
            parent_spl.setSizes([max(dim // n, 50)] * n)
        else:
            # Different (or missing) orientation: wrap active pane in a new sub-splitter
            if not isinstance(parent_spl, QSplitter):
                # Fallback — should not happen in normal use
                self._splitter.addWidget(new_pane)
                return new_pane

            idx = parent_spl.indexOf(active)
            parent_sizes = parent_spl.sizes()

            sub = self._make_sub_splitter(orientation)
            # Detach active from its current parent and move it into the sub-splitter
            active.setParent(None)   # removes from parent_spl; idx slot is now vacant
            sub.addWidget(active)
            sub.addWidget(new_pane)
            sub.setSizes([1, 1])     # equal initial split

            parent_spl.insertWidget(idx, sub)
            parent_spl.setSizes(parent_sizes)  # restore parent distribution

        return new_pane

    # ── Nav ───────────────────────────────────────────────────────────────────

    def _on_nav_index_changed(self, idx: int):
        self._side_stack.setCurrentIndex(idx)

    # ── Tab factories ─────────────────────────────────────────────────────────

    def open_cloudwatch_tab(self, cfg: dict, split: str = "tab"):
        worker = TailWorker(
            cfg["client"], cfg["group"], cfg["stream"],
            cfg["filter"], cfg["interval"], cfg["lookback"],
        )
        viewer = LogViewer(source_type="cloudwatch")
        stream_label = cfg["stream"] or "(all streams)"
        viewer.set_title(f"{cfg['group']}  ›  {stream_label}")
        tab_title = (cfg["stream"] or cfg["group"]).split("/")[-1]
        self._add_tab(tab_title, viewer, worker, split=split)

    def open_file_tab(self, path: str, tail_lines: int = 100, split: str = "tab"):
        worker = FileWorker(path, tail_lines=tail_lines)
        viewer = LogViewer(source_type="file")
        viewer.set_title(path)
        self._add_tab(os.path.basename(path), viewer, worker, split=split)

    def open_stdin_tab(self):
        worker = StdinWorker()
        viewer = LogViewer(source_type="stdin")
        viewer.set_title("stdin — piped input")
        self._add_tab("stdin", viewer, worker, split="tab")

    # ── Internal tab management ───────────────────────────────────────────────

    def _add_tab(self, title: str, viewer: LogViewer, worker, split: str = "tab"):
        worker.new_lines.connect(viewer.append_events)
        worker.status.connect(self._status.showMessage)
        worker.error.connect(lambda msg, v=viewer: self._on_error(msg, v))
        if hasattr(worker, "history_done"):
            worker.history_done.connect(
                lambda n: self._status.showMessage(i18n.tr("history_loaded", n=n))
            )
        viewer.stop_requested.connect(lambda v=viewer: self._stop_viewer(v))
        viewer.stop_btn.setEnabled(True)

        if split == "vertical":
            target = self._get_or_create_secondary_pane(Qt.Orientation.Horizontal)
        elif split == "horizontal":
            target = self._get_or_create_secondary_pane(Qt.Orientation.Vertical)
        else:
            target = self._active_pane

        self._workers[id(viewer)] = worker
        idx = target.addTab(viewer, title)
        target.setCurrentIndex(idx)
        self._active_pane = target
        worker.start()

    def _close_tab(self, index: int, tabs: QTabWidget):
        viewer = tabs.widget(index)
        self._stop_viewer(viewer)
        tabs.removeTab(index)
        # Remove empty secondary panes (keep at least one pane)
        if tabs.count() == 0 and tabs in self._panes and len(self._panes) > 1:
            self._panes.remove(tabs)
            tabs.setParent(None)  # type: ignore[call-overload]
            if self._active_pane is tabs:
                self._active_pane = self._panes[0]

    def _stop_viewer(self, viewer: LogViewer):
        worker = self._workers.pop(id(viewer), None)
        if worker and worker.isRunning():
            worker.stop()
            worker.wait(3000)
        if viewer:
            viewer.stop_btn.setEnabled(False)

    def _on_error(self, msg: str, viewer: LogViewer):
        self._stop_viewer(viewer)
        self._status.showMessage(i18n.tr("err_prefix", msg=msg))
        QMessageBox.critical(self, i18n.tr("err_worker"), msg)

    def closeEvent(self, event):  # noqa: N802
        for worker in list(self._workers.values()):
            if worker.isRunning():
                worker.stop()
                worker.wait(2000)
        event.accept()


# ── Tiny helpers ──────────────────────────────────────────────────────────────

def _field_label(text: str) -> QLabel:
    """Small field caption label."""
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {C_MUTED}; font-size: 11px; background: transparent; border: none;"
    )
    return lbl
