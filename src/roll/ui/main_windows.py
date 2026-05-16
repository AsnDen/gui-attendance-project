import logging
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QStatusBar, QLabel, QMessageBox,
    QToolBar, QMenuBar, QMenu, QComboBox, QLineEdit, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon

from roll.ui.styles import MAIN_WINDOW_STYLE, TABLE_STYLE, STATUS_BAR_STYLE, BUTTON_STYLE
from roll.ui.qr_scanner_dialog import QRScannerDialog
from roll.services.person_service import PersonService
from roll.services.event_service import EventService
from roll.services.attendance_service import AttendanceService
from roll.services.identifier_service import IdentifierService
from roll.services.verification_service import VerificationService
from roll.services.qr_generator_service import QRGeneratorService
from roll.repositories.person_repository import PersonRepository
from roll.repositories.event_repository import EventRepository
from roll.repositories.attendance_repository import AttendanceRepository
from roll.repositories.identifier_repository import IdentifierRepository
from roll.core import IdentifierType, IdentifierUpdateDTO

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self._init_services()
        
  
        self.setWindowTitle("Roll - Attendance System")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._setup_status_bar()
        self._setup_central_widget()
        self._setup_timer()
        
        self._load_persons()
        self._load_events()
        self._load_identifiers_selector()
        
        logger.info("Main window initialized")
    
    def _init_services(self):
        """Initialize services and repositories."""
        self.person_repo = PersonRepository()
        self.event_repo = EventRepository()
        self.attendance_repo = AttendanceRepository()
        self.identifier_repo = IdentifierRepository()
        
        self.person_service = PersonService(self.person_repo)
        self.event_service = EventService(self.event_repo)
        self.attendance_service = AttendanceService(self.attendance_repo)
        self.verification_service = VerificationService(self.identifier_repo)
        self.identifier_service = IdentifierService(self.identifier_repo)
        self.qr_generator = QRGeneratorService()
        
        logger.info("Services initialized")
        
    def _setup_menu_bar(self):
        """Setup application menu bar."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        attendance_menu = menubar.addMenu("&Attendance")
        
        scan_action = QAction("&Scan QR Code", self)
        scan_action.setShortcut("F2")
        scan_action.triggered.connect(self._open_scanner)
        attendance_menu.addAction(scan_action)
        
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_data)
        view_menu.addAction(refresh_action)
        
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_tool_bar(self):
        """Setup toolbar with actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        scan_action = QAction("Scan QR", self)
        scan_action.triggered.connect(self._open_scanner)
        toolbar.addAction(scan_action)
        
        toolbar.addSeparator()
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self._refresh_data)
        toolbar.addAction(refresh_action)
    
    def _setup_central_widget(self):
        """Setup central widget with tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Button panel
        button_layout = QHBoxLayout()
        
        self.scan_button = QPushButton("Scan QR Code")
        self.scan_button.setStyleSheet(BUTTON_STYLE)
        self.scan_button.clicked.connect(self._open_scanner)
        button_layout.addWidget(self.scan_button)
        
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setStyleSheet(BUTTON_STYLE)
        self.refresh_button.clicked.connect(self._refresh_data)
        button_layout.addWidget(self.refresh_button)
        
        # Current event selector
        button_layout.addStretch()
        button_layout.addWidget(QLabel("Current Event:"))
        self.current_event_combo = QComboBox()
        self.current_event_combo.setMinimumWidth(200)
        button_layout.addWidget(self.current_event_combo)
        
        layout.addLayout(button_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self._setup_attendance_tab()
        self._setup_persons_tab()
        self._setup_events_tab()
        self._setup_identifiers_tab()
    
    def _setup_attendance_tab(self):
        """Setup attendance table tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.attendance_table = QTableWidget()
        self.attendance_table.setStyleSheet(TABLE_STYLE)
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels([
            "ID", "Person", "Event", "Status"
        ])
        self.attendance_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.attendance_table)
        self.tab_widget.addTab(widget, "Attendance")
    
    def _setup_persons_tab(self):
        """Setup persons table tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar for persons
        persons_toolbar = QHBoxLayout()
        
        self.add_person_btn = QPushButton("Add Person")
        self.add_person_btn.clicked.connect(self._add_person)
        persons_toolbar.addWidget(self.add_person_btn)
        
        self.edit_person_btn = QPushButton("Edit Person")
        self.edit_person_btn.clicked.connect(self._edit_person)
        persons_toolbar.addWidget(self.edit_person_btn)
        
        self.delete_person_btn = QPushButton("Delete Person")
        self.delete_person_btn.clicked.connect(self._delete_person)
        persons_toolbar.addWidget(self.delete_person_btn)
        
        self.show_qr_btn = QPushButton("Show QR Code")
        self.show_qr_btn.clicked.connect(self._show_person_qr)
        self.show_qr_btn.setStyleSheet("background-color: #2d6a4f;")
        persons_toolbar.addWidget(self.show_qr_btn)
        
        persons_toolbar.addStretch()
        layout.addLayout(persons_toolbar)
        
        self.persons_table = QTableWidget()
        self.persons_table.setStyleSheet(TABLE_STYLE)
        self.persons_table.setColumnCount(3)
        self.persons_table.setHorizontalHeaderLabels([
            "ID", "Label", "Description"
        ])
        self.persons_table.horizontalHeader().setStretchLastSection(True)
        self.persons_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Убран двойной клик: self.persons_table.itemDoubleClicked.connect(self._show_person_qr)
        
        layout.addWidget(self.persons_table)
        self.tab_widget.addTab(widget, "Persons")
    
    def _setup_events_tab(self):
        """Setup events table tab with controls."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Toolbar for events
        events_toolbar = QHBoxLayout()
        
        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(self._add_event)
        events_toolbar.addWidget(self.add_event_btn)
        
        self.edit_event_btn = QPushButton("Edit Event")
        self.edit_event_btn.clicked.connect(self._edit_event)
        events_toolbar.addWidget(self.edit_event_btn)
        
        self.delete_event_btn = QPushButton("Delete Event")
        self.delete_event_btn.clicked.connect(self._delete_event)
        events_toolbar.addWidget(self.delete_event_btn)
        
        events_toolbar.addStretch()
        layout.addLayout(events_toolbar)
        
        # Events table
        self.events_table = QTableWidget()
        self.events_table.setStyleSheet(TABLE_STYLE)
        self.events_table.setColumnCount(5)
        self.events_table.setHorizontalHeaderLabels([
            "ID", "Event Name", "Description", "Start Time", "Duration"
        ])
        self.events_table.horizontalHeader().setStretchLastSection(True)
        self.events_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.events_table)
        self.tab_widget.addTab(widget, "Events")
    
    def _setup_identifiers_tab(self):
        """Setup identifiers management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Person selector
        person_layout = QHBoxLayout()
        person_layout.addWidget(QLabel("Select Person:"))
        self.identifier_person_combo = QComboBox()
        self.identifier_person_combo.setMinimumWidth(200)
        self.identifier_person_combo.currentIndexChanged.connect(self._load_identifiers)
        person_layout.addWidget(self.identifier_person_combo)
        person_layout.addStretch()
        layout.addLayout(person_layout)
        
        # Add identifier section
        add_group = QHBoxLayout()
        self.identifier_hash_edit = QLineEdit()
        self.identifier_hash_edit.setPlaceholderText("QR Code / Card ID")
        add_group.addWidget(self.identifier_hash_edit)
        
        self.identifier_type_combo = QComboBox()
        self.identifier_type_combo.addItems(["QR", "CARD"])
        add_group.addWidget(self.identifier_type_combo)
        
        self.add_identifier_btn = QPushButton("Add Identifier")
        self.add_identifier_btn.clicked.connect(self._add_identifier)
        add_group.addWidget(self.add_identifier_btn)
        
        layout.addLayout(add_group)
        
        # Identifiers table
        self.identifiers_table = QTableWidget()
        self.identifiers_table.setStyleSheet(TABLE_STYLE)
        self.identifiers_table.setColumnCount(3)
        self.identifiers_table.setHorizontalHeaderLabels([
            "ID", "Type", "Hash Value"
        ])
        self.identifiers_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.identifiers_table)
        
        self.delete_identifier_btn = QPushButton("Delete Selected")
        self.delete_identifier_btn.clicked.connect(self._delete_identifier)
        layout.addWidget(self.delete_identifier_btn)
        
        self.tab_widget.addTab(widget, "Identifiers")
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet(STATUS_BAR_STYLE)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
    
    def _setup_timer(self):
        """Setup timer for updating time and status."""
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
    
    def _update_time(self):
        """Update time display in status bar."""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def _open_scanner(self):
        """Open QR scanner dialog."""
        logger.info("Opening QR scanner")
        self.status_label.setText("Opening QR scanner...")
        
        dialog = QRScannerDialog(self)
        if dialog.exec():
            result = dialog.get_scanned_data()
            if result:
                self.status_label.setText(f"QR Scanned: {result}")
                self._process_scanned_identifier(result)
            else:
                self.status_label.setText("QR scan cancelled or failed")
        else:
            self.status_label.setText("QR scan cancelled")
    
    def _process_scanned_identifier(self, identifier: str):
        """Process scanned QR code and mark attendance."""
        logger.info(f"Processing identifier: {identifier}")
        
        if identifier.startswith("ROLL:"):
            parts = identifier.split(":")
            if len(parts) >= 2:
                try:
                    person_id = int(parts[1])
                    person = self.person_service.get_person(person_id)
                    if person:
                        current_event_id = self.current_event_combo.currentData()
                        if not current_event_id:
                            QMessageBox.warning(self, "No Event Selected", "Please select a current event.", QMessageBox.Ok)
                            return
                        
                        self.attendance_service.mark_attendance(person_id, current_event_id)
                        QMessageBox.information(self, "Attendance Recorded", f"Attendance marked for:\n{person.label}", QMessageBox.Ok)
                        self.status_label.setText(f"Attendance recorded for {person.label}")
                        self._refresh_data()
                        return
                except Exception as e:
                    logger.error(f"Error parsing QR: {e}")
        
        QMessageBox.warning(self, "Invalid QR Code", "This QR code is not registered.", QMessageBox.Ok)
        self.status_label.setText("Invalid QR code")
    
    def _load_persons(self):
        """Load persons data into table."""
        try:
            persons = self.person_service.get_all_persons()
            self.persons_table.setRowCount(len(persons))
            
            for row, person in enumerate(persons):
                self.persons_table.setItem(row, 0, QTableWidgetItem(str(person.person_id)))
                self.persons_table.setItem(row, 1, QTableWidgetItem(person.label))
                self.persons_table.setItem(row, 2, QTableWidgetItem(person.description or ""))
            
            self.persons_table.resizeColumnsToContents()
            logger.info(f"Loaded {len(persons)} persons")
        except Exception as e:
            logger.error(f"Error loading persons: {e}")
            self.status_label.setText(f"Error loading persons: {e}")
    
    def _load_events(self):
        """Load events into table and combo box."""
        try:
            events = self.event_service.get_all_events()
            self.events_table.setRowCount(len(events))
            
            for row, event in enumerate(events):
                self.events_table.setItem(row, 0, QTableWidgetItem(str(event.event_id)))
                self.events_table.setItem(row, 1, QTableWidgetItem(event.label))
                self.events_table.setItem(row, 2, QTableWidgetItem(event.description or ""))
                self.events_table.setItem(row, 3, QTableWidgetItem(event.start_time.strftime("%Y-%m-%d %H:%M")))
                self.events_table.setItem(row, 4, QTableWidgetItem(f"{event.duration.seconds // 60} min"))
            
            self.current_event_combo.clear()
            for event in events:
                self.current_event_combo.addItem(f"{event.label} ({event.start_time.strftime('%Y-%m-%d')})", event.event_id)
            
            logger.info(f"Loaded {len(events)} events")
        except Exception as e:
            logger.error(f"Error loading events: {e}")
    
    def _load_identifiers_selector(self):
        """Load persons into selector combo box."""
        try:
            persons = self.person_service.get_all_persons()
            self.identifier_person_combo.clear()
            for person in persons:
                self.identifier_person_combo.addItem(f"{person.label} (ID: {person.person_id})", person.person_id)
        except Exception as e:
            logger.error(f"Error loading person selector: {e}")
    
    def _load_identifiers(self):
        """Load identifiers for selected person using repository."""
        person_id = self.identifier_person_combo.currentData()
        if not person_id:
            self.identifiers_table.setRowCount(0)
            return
        
        try:
            identifiers = self.identifier_repo.get_by_person(person_id)
            
            self.identifiers_table.setRowCount(len(identifiers))
            for row, identifier in enumerate(identifiers):
                self.identifiers_table.setItem(row, 0, QTableWidgetItem(str(identifier.identifier_id)))
                self.identifiers_table.setItem(row, 1, QTableWidgetItem(identifier.__class__.__name__.replace("Identifier", "")))
                hash_display = identifier.hash_value[:20] + "..." if len(identifier.hash_value) > 20 else identifier.hash_value
                self.identifiers_table.setItem(row, 2, QTableWidgetItem(hash_display))
        except Exception as e:
            logger.error(f"Error loading identifiers: {e}")
    
    def _add_person(self):
        """Add new person with manual ID."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Person")
        dialog.setModal(True)
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()
        
        id_edit = QLineEdit()
        id_edit.setPlaceholderText("Enter ID (number)")
        form_layout.addRow("ID:", id_edit)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter person name")
        form_layout.addRow("Name:", name_edit)
        
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Optional description")
        form_layout.addRow("Description:", desc_edit)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            id_text = id_edit.text().strip()
            label = name_edit.text().strip()
            description = desc_edit.text().strip() or None
            
            if not id_text:
                QMessageBox.warning(self, "Warning", "ID cannot be empty")
                return
            
            if not label:
                QMessageBox.warning(self, "Warning", "Person name cannot be empty")
                return
            
            try:
                person_id = int(id_text)
                
                try:
                    existing = self.person_service.get_person(person_id)
                    if existing:
                        QMessageBox.warning(self, "Warning", f"Person with ID {person_id} already exists!")
                        return
                except:
                    pass  
                
                self.person_service.add_person_with_id(person_id, label, description)
                logger.info(f"Person added with ID: {person_id}")
                
                self._load_persons()
                
                qr_data = f"ROLL:{person_id}:{label}"
                
                from roll.core import IdentifierUpdateDTO
                identifier_dto = IdentifierUpdateDTO(
                    hash_value=qr_data,
                    person_id=person_id,
                    identifier_type=IdentifierType.QR
                )
                self.identifier_repo.add(identifier_dto)
                
                self.qr_generator.generate_qr_for_person(person_id, label)
                
                self._load_identifiers_selector()
                self.status_label.setText(f"Person '{label}' added with ID: {person_id} and QR code")
                
                reply = QMessageBox.question(
                    self, "QR Code Generated",
                    f"QR code for '{label}' generated. View now?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    for row in range(self.persons_table.rowCount()):
                        if int(self.persons_table.item(row, 0).text()) == person_id:
                            self.persons_table.selectRow(row)
                            break
                    self._show_person_qr()
                    
            except ValueError:
                QMessageBox.warning(self, "Warning", "ID must be a number")
            except Exception as e:
                logger.error(f"Failed to add person: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add person: {e}")
    
    def _edit_person(self):
        """Edit selected person."""
        current_row = self.persons_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select a person to edit")
            return
        
        person_id = int(self.persons_table.item(current_row, 0).text())
        current_label = self.persons_table.item(current_row, 1).text()
        
        label, ok = QInputDialog.getText(self, "Edit Person", "Person Name:", text=current_label)
        if ok and label and label.strip():
            try:
                from roll.core import PersonUpdateDTO
                update_dto = PersonUpdateDTO(label=label.strip())
                self.person_service.update_person(person_id, update_dto)
                self._load_persons()
                self._load_identifiers_selector()
                self.status_label.setText(f"Person updated")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to edit person: {e}")
    
    def _delete_person(self):
        """Delete selected person."""
        current_row = self.persons_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select a person to delete")
            return
        
        person_id = int(self.persons_table.item(current_row, 0).text())
        person_name = self.persons_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete person '{person_name}'?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.qr_generator.delete_qr_for_person(person_id)
                self.person_service.delete_person(person_id)
                self._load_persons()
                self._load_identifiers_selector()
                self._load_identifiers()
                self.status_label.setText(f"Person '{person_name}' deleted")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete person: {e}")
    
    def _show_person_qr(self):
        """Show QR code for selected person (only by button click)."""
        current_row = self.persons_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select a person first")
            return
        
        person_id = int(self.persons_table.item(current_row, 0).text())
        person_name = self.persons_table.item(current_row, 1).text()
        
        from roll.ui.person_qr_dialog import PersonQRDialog
        dialog = PersonQRDialog(self, person_id=person_id, person_name=person_name)
        dialog.exec()
    
    def _add_event(self):
        """Add new event."""
        from roll.ui.event_dialog import EventDialog
        
        dialog = EventDialog(self)
        if dialog.exec():
            data = dialog.get_event_data()
            try:
                self.event_service.add_event(
                    label=data['label'],
                    start_time=data['start_time'],
                    duration=data['duration'],
                    description=data['description']
                )
                self._load_events()
                self._refresh_data()
                self.status_label.setText(f"Event '{data['label']}' added")
            except Exception as e:
                logger.error(f"Failed to add event: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add event: {e}")
    
    def _edit_event(self):
        """Edit selected event."""
        current_row = self.events_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select an event to edit")
            return
        
        event_id = int(self.events_table.item(current_row, 0).text())
        try:
            event = self.event_service.get_event(event_id)
            
            from roll.ui.event_dialog import EventDialog
            dialog = EventDialog(self, event_data=event)
            if dialog.exec():
                data = dialog.get_event_data()
                from roll.core import EventUpdateDTO
                update_dto = EventUpdateDTO(
                    label=data['label'],
                    start_time=data['start_time'],
                    duration=data['duration'],
                    description=data['description']
                )
                self.event_service.update_event(event_id, update_dto)
                self._load_events()
                self._refresh_data()
                self.status_label.setText(f"Event '{data['label']}' updated")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit event: {e}")
    
    def _delete_event(self):
        """Delete selected event."""
        current_row = self.events_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select an event to delete")
            return
        
        event_id = int(self.events_table.item(current_row, 0).text())
        event_name = self.events_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete event '{event_name}'?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.event_service.delete_event(event_id)
                self._load_events()
                self._refresh_data()
                self.status_label.setText(f"Event '{event_name}' deleted")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete event: {e}")
    
    def _add_identifier(self):
        """Add identifier for selected person."""
        person_id = self.identifier_person_combo.currentData()
        if not person_id:
            QMessageBox.warning(self, "Warning", "Please select a person")
            return
        
        hash_value = self.identifier_hash_edit.text().strip()
        if not hash_value:
            QMessageBox.warning(self, "Warning", "Please enter hash value or scan QR code")
            return
        
        identifier_type_str = self.identifier_type_combo.currentText()
        identifier_type = IdentifierType.QR if identifier_type_str == "QR" else IdentifierType.CARD
        
        try:
            self.identifier_service.add_identifier(hash_value, person_id, identifier_type)
            self.identifier_hash_edit.clear()
            self._load_identifiers()
            self.status_label.setText(f"Identifier added for person ID {person_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add identifier: {e}")
    
    def _delete_identifier(self):
        """Delete selected identifier."""
        current_row = self.identifiers_table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "Info", "Please select an identifier to delete")
            return
        
        identifier_id = int(self.identifiers_table.item(current_row, 0).text())
        
        reply = QMessageBox.question(self, "Confirm Delete", "Delete this identifier?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.identifier_service.delete_identifier(identifier_id)
                self._load_identifiers()
                self.status_label.setText("Identifier deleted")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete identifier: {e}")
    
    def _refresh_data(self):
        """Refresh all data in tables."""
        logger.info("Refreshing data")
        self.status_label.setText("Refreshing data...")
        
        self._load_persons()
        self._load_events()
        self._load_identifiers_selector()
        self._load_identifiers()
        
        self.status_label.setText("Data refreshed")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Roll",
            "Roll - Attendance Management System\n\n"
            "Version: 1.0.0\n\n"
            "A system for managing attendance using QR codes.\n"
            "Built with PySide6 and SQLite."
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Closing main window")
        event.accept()