from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from roll.core import BaseEvent, AttendanceStatus
from roll.services import AttendanceService, PersonService


class EventDetailsPanel(QFrame):
    mark_attendance_requested = Signal(object)
    manual_mark_requested = Signal(object)

    def __init__(self, attendance_service: AttendanceService,
                 person_service: PersonService) -> None:
        super().__init__()
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._current_event: BaseEvent | None = None
        self._row_for_person = {}
        self._setup_ui()
        self._update_ui()

    def _setup_ui(self) -> None:
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        self.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 12px;
                margin: 5px;
            }
            QLabel#title {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #34495e;
                border-radius: 8px;
            }
            QLabel#info {
                color: #ecf0f1;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #16a085;
                color: white;
            }
            QTableWidget {
                background-color: #34495e;
                alternate-background-color: #2c3e50;
                color: #ecf0f1;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        self._title_label = QLabel("ДЕТАЛИ ПРЕДМЕТА")
        self._title_label.setObjectName("title")
        self._title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_label)

        self._info_label = QLabel("Выберите предмет из расписания")
        self._info_label.setObjectName("info")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        self._qr_btn = QPushButton("Отметить по QR")
        self._qr_btn.clicked.connect(self._on_qr_clicked)
        self._qr_btn.setEnabled(False)

        self._manual_btn = QPushButton("Отметить вручную")
        self._manual_btn.clicked.connect(self._on_manual_clicked)
        self._manual_btn.setEnabled(False)

        layout.addWidget(self._qr_btn)
        layout.addWidget(self._manual_btn)

        self._table = QTableWidget()
        self._table.setColumnCount(1)
        self._table.setHorizontalHeaderLabels([""])
        self._table.horizontalHeader().setVisible(False)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._table)

    def _on_qr_clicked(self):
        if self._current_event:
            self.mark_attendance_requested.emit(self._current_event)

    def _on_manual_clicked(self):
        if self._current_event:
            self.manual_mark_requested.emit(self._current_event)

    def _on_item_double_clicked(self, item):
        if not self._current_event:
            return
        row = item.row()
        person_id = self._row_for_person.get(row)
        if person_id:
            self._toggle_member(person_id)

    def _toggle_member(self, person_id: int):
        if not self._current_event:
            return
        attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._current_event.event_id)}
        existing = attendances.get(person_id)
        if existing and existing.status == AttendanceStatus.PRESENT:
            self._attendance_service.update_attendance(existing.attendance_id, AttendanceStatus.ABSENT)
        else:
            self._attendance_service.add_attendance(person_id, self._current_event.event_id, AttendanceStatus.PRESENT)
        self._update_ui()

    def set_event(self, event: BaseEvent | None):
        self._current_event = event
        self._update_ui()

    def _update_ui(self):
        if not self._current_event:
            self._info_label.setText("Выберите предмет из расписания")
            self._qr_btn.setEnabled(False)
            self._manual_btn.setEnabled(False)
            self._table.clear()
            self._table.setRowCount(0)
            self._row_for_person.clear()
            return

        duration_min = self._current_event.duration.seconds // 60
        info_text = (
            f"Предмет: {self._current_event.label}\n"
            f"Тема: {self._current_event.description or '(не указана)'}\n"
            f"Время: {self._current_event.start_time.strftime('%H:%M')} ({duration_min} мин)"
        )
        self._info_label.setText(info_text)
        self._qr_btn.setEnabled(True)
        self._manual_btn.setEnabled(True)

        persons = list(self._person_service.get_all_persons())
        persons.sort(key=lambda p: p.label.lower())

        try:
            attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._current_event.event_id)}
        except Exception:
            attendances = {}

        self._table.setRowCount(len(persons))
        self._row_for_person.clear()
        for row, person in enumerate(persons):
            self._row_for_person[row] = person.person_id
            item = QTableWidgetItem(person.label)
            is_present = person.person_id in attendances and attendances[person.person_id].status == AttendanceStatus.PRESENT
            if is_present:
                item.setForeground(QColor("#27ae60"))
            else:
                item.setForeground(QColor("#e74c3c"))
            self._table.setItem(row, 0, item)

    def mark_person(self, person_id: int):
        self._update_ui()

    def refresh(self):
        self._update_ui()
