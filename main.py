#!/usr/bin/env python3
"""
SimpleLog — multi-source log viewer
Usage:
  simplelog                              → CloudWatch GUI
  simplelog /path/to/file.log           → tail file(s) in tabs
  command | simplelog                   → read piped stdin
  simplelog --split vertical f1 f2      → open f1 & f2 side by side
  simplelog --split horizontal f1 f2    → open f1 & f2 top/bottom
"""
import argparse
import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from ui import MainWindow
from ui import apply_style as apply_dark_palette


def main():
    parser = argparse.ArgumentParser(
        prog="simplelog",
        description="SimpleLog — multi-source log viewer",
        add_help=False,
    )
    parser.add_argument(
        "--split",
        choices=["tab", "vertical", "horizontal"],
        default="tab",
        metavar="MODE",
        help="How to open logs: tab (default), vertical (side by side), horizontal (top/bottom)",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=100,
        metavar="N",
        help="Number of lines to load from the end of each file (default: 100)",
    )
    parser.add_argument("files", nargs="*", help="Log file paths to open")
    args, _ = parser.parse_known_args()

    app = QApplication(sys.argv)
    app.setApplicationName("SimpleLog")
    app.setStyle("Fusion")
    apply_dark_palette(app)

    window = MainWindow()
    window.show()

    # Detect piped stdin (not a terminal)
    stdin_is_pipe = not sys.stdin.isatty()

    def _open_initial_tabs():
        if stdin_is_pipe:
            window.open_stdin_tab()
        for path in args.files:
            if os.path.isfile(path):
                window.open_file_tab(path, args.tail, args.split)
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(window, "File not found", f"Cannot open: {path}")

    QTimer.singleShot(100, _open_initial_tabs)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
