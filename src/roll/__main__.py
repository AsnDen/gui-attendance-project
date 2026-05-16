"""Program entry point."""

import sys
import logging
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap

from roll.core import init_database, setup_logging
from roll.ui.main_windows import MainWindow


def main() -> None:
    """Program entry point."""
    # Setup logging first
    setup_logging()
    logger = logging.getLogger("roll")
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Roll")
    app.setOrganizationName("Roll")
    app.setApplicationVersion("1.0.0")
    
    # Show splash screen (optional)
    # splash = QSplashScreen()
    # splash.show()
    # splash.showMessage("Loading database...", Qt.AlignmentFlag.AlignBottom)
    
    logger.info("Starting Roll application")
    
    # Initialize database
    try:
        db = init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # splash.close()
        raise
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Close splash after window shows
    # QTimer.singleShot(1000, splash.close)
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
