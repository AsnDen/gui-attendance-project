"""UI module for Roll application."""

from roll.ui.main_windows import MainWindow
from roll.ui.qr_scanner_dialog import QRScannerDialog
from roll.ui.person_qr_dialog import PersonQRDialog
from roll.ui.event_dialog import EventDialog
from roll.ui.styles import (
    MAIN_WINDOW_STYLE,
    TABLE_STYLE,
    STATUS_BAR_STYLE,
    BUTTON_STYLE,
    SCANNER_DIALOG_STYLE
)

__all__ = [
    "MainWindow",
    "QRScannerDialog",
    "PersonQRDialog",
    "EventDialog",
    "MAIN_WINDOW_STYLE",
    "TABLE_STYLE",
    "STATUS_BAR_STYLE",
    "BUTTON_STYLE",
    "SCANNER_DIALOG_STYLE",
]