"""Dialog for adding/editing events."""

from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QDateTimeEdit, QSpinBox,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


class EventDialog(QDialog):
    """Dialog for creating or editing events."""
    
    def __init__(self, parent=None, event_data=None):  # Изменено: event -> event_data
        super().__init__(parent)
        self.event_data = event_data  # Изменено: self.event -> self.event_data
        self.setWindowTitle("Add Event" if not event_data else "Edit Event")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        if event_data:  # Изменено: if event -> if event_data
            self._load_event_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow("Event Name:", self.name_edit)
        
        # Description field
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.desc_edit)
        
        # Start time
        self.start_time = QDateTimeEdit()
        self.start_time.setDateTime(datetime.now())
        self.start_time.setCalendarPopup(True)
        form_layout.addRow("Start Time:", self.start_time)
        
        # Duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 480)  # 1 minute to 8 hours
        self.duration_spin.setSuffix(" minutes")
        self.duration_spin.setValue(60)
        form_layout.addRow("Duration:", self.duration_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _load_event_data(self):
        """Load event data into fields."""
        self.name_edit.setText(self.event_data.label)
        if self.event_data.description:
            self.desc_edit.setText(self.event_data.description)
        self.start_time.setDateTime(self.event_data.start_time)
        self.duration_spin.setValue(self.event_data.duration.seconds // 60)
    
    def _save(self):
        """Validate and save event data."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Event name is required")
            return
        
        self.accept()
    
    def get_event_data(self):
        """Get event data from dialog."""
        return {
            'label': self.name_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip() or None,
            'start_time': self.start_time.dateTime().toPython(),
            'duration': timedelta(minutes=self.duration_spin.value())
        }