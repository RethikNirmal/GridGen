#!/usr/bin/env python3
"""Main entry point for the Grid Connection Game."""

import sys

from PyQt6.QtWidgets import QApplication

from src.gui.main_window import MainWindow


def main() -> None:
    """Main function to start the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Grid Connection Game")
    app.setApplicationVersion("1.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
