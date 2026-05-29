from PySide6.QtWidgets import QDialog

DIALOG_STYLE = """
    QDialog {
        background-color: #2c3e50;
        color: #ecf0f1;
    }
    QLabel {
        color: #ecf0f1;
    }
    QLineEdit, QTimeEdit, QSpinBox, QComboBox {
        background-color: #34495e;
        color: #ecf0f1;
        border: 1px solid #1abc9c;
        border-radius: 4px;
        padding: 5px;
    }
    QPushButton {
        background-color: #1abc9c;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: #2c3e50;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #16a085;
        color: white;
    }
    QTableWidget {
        background-color: #34495e;
        alternate-background-color: #2c3e50;
        color: #ecf0f1;
        gridline-color: #1abc9c;
    }
    QHeaderView::section {
        background-color: #1abc9c;
        color: #2c3e50;
        font-weight: bold;
    }
"""

class BaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(DIALOG_STYLE)