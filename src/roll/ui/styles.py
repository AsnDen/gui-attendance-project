"""Application styles and themes."""

MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
}

QMenuBar {
    background-color: #3c3c3c;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #4a4a4a;
}

QMenu {
    background-color: #3c3c3c;
    color: #ffffff;
}

QMenu::item:selected {
    background-color: #4a4a4a;
}
"""

SCANNER_DIALOG_STYLE = """
QDialog {
    background-color: #2b2b2b;
}

QLabel#video_label {
    background-color: #000000;
    border: 2px solid #4a4a4a;
    border-radius: 5px;
}

QLabel#status_label {
    color: #ffffff;
    font-size: 14px;
    padding: 10px;
}

QPushButton {
    background-color: #4a4a4a;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #5a5a5a;
}

QPushButton:pressed {
    background-color: #3a3a3a;
}

QPushButton#scan_button {
    background-color: #2d6a4f;
    font-weight: bold;
}

QPushButton#scan_button:hover {
    background-color: #40916c;
}

QPushButton#stop_button {
    background-color: #9d0208;
}

QPushButton#stop_button:hover {
    background-color: #dc2f02;
}
"""

TABLE_STYLE = """
QTableWidget {
    background-color: #3c3c3c;
    color: #ffffff;
    gridline-color: #4a4a4a;
    selection-background-color: #2d6a4f;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: #2d6a4f;
}

QHeaderView::section {
    background-color: #2b2b2b;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #4a4a4a;
}

QTableCornerButton::section {
    background-color: #2b2b2b;
}
"""

STATUS_BAR_STYLE = """
QStatusBar {
    background-color: #3c3c3c;
    color: #ffffff;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #4a4a4a;
    color: #ffffff;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #5a5a5a;
}

QPushButton:pressed {
    background-color: #3a3a3a;
}
"""