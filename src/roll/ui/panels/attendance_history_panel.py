# src/roll/ui/panels/attendance_history_panel.py
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from roll.core import AttendanceStatus
from roll.services import AttendanceService, PersonService, EventService


class AttendanceHistoryPanel(QFrame):
    def __init__(self, attendance_service: AttendanceService,
                 person_service: PersonService,
                 event_service: EventService):
        super().__init__()
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._event_service = event_service
        self._current_event = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 12px;
                margin: 5px;
            }
            QLabel#title {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2c3e50;
                border-radius: 8px;
            }
            QTableWidget {
                background-color: #2c3e50;
                alternate-background-color: #34495e;
                color: #ecf0f1;
                gridline-color: #1abc9c;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._title_label = QLabel("ИСТОРИЯ ПОСЕЩАЕМОСТИ")
        self._title_label.setObjectName("title")
        self._title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_label)

        btn_layout = QHBoxLayout()
        self._all_btn = QPushButton("Все даты")
        self._last5_btn = QPushButton("Последние 5 занятий")
        self._all_btn.clicked.connect(lambda: self.load_history(all_dates=True))
        self._last5_btn.clicked.connect(lambda: self.load_history(all_dates=False))
        btn_layout.addWidget(self._all_btn)
        btn_layout.addWidget(self._last5_btn)
        layout.addLayout(btn_layout)

        self._table = QTableWidget()
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self._table.horizontalHeader().setSectionsMovable(False)
        self._table.verticalHeader().setVisible(False)
        # Разрешаем перенос текста в заголовках (на случай длинных дат)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self._table)

        self._info_label = QLabel("Выберите предмет в расписании")
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setStyleSheet("color: #1abc9c;")
        layout.addWidget(self._info_label)

    def set_event(self, event):
        self._current_event = event
        if event:
            self._title_label.setText(f"ИСТОРИЯ ПОСЕЩАЕМОСТИ: {event.label}")
            self.load_history(all_dates=True)
        else:
            self._title_label.setText("ИСТОРИЯ ПОСЕЩАЕМОСТИ")
            self._table.clear()
            self._table.setRowCount(0)
            self._info_label.setText("Выберите предмет в расписании")

    def load_history(self, all_dates: bool = True):
        if not self._current_event:
            return

        subject_label = self._current_event.label
        all_events = self._event_service.get_all_events()
        subject_events = [e for e in all_events if e.label == subject_label]
        if not subject_events:
            self._table.clear()
            self._table.setRowCount(0)
            self._info_label.setText("Нет других занятий по этому предмету")
            return

        # Сортировка событий по времени (от старых к новым)
        subject_events.sort(key=lambda e: e.start_time)
        if not all_dates:
            subject_events = subject_events[-5:]

        # Сортировка участников по алфавиту
        persons = list(self._person_service.get_all_persons())
        persons.sort(key=lambda p: p.label.lower())

        # Настройка столбцов
        self._table.setColumnCount(len(subject_events) + 1)
        # Первый столбец: ФИО (широкий, фиксированный)
        self._table.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.setColumnWidth(0, 500)  # ширина столбца ФИО 500 пикселей
        # Остальные столбцы — даты занятий
        for col, ev in enumerate(subject_events, start=1):
            date_str = ev.start_time.strftime("%d.%m.%Y")
            self._table.setHorizontalHeaderItem(col, QTableWidgetItem(date_str))
            self._table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
            self._table.horizontalHeader().setMinimumSectionSize(90)  # минимальная ширина для даты

        self._table.setRowCount(len(persons))

        for row, person in enumerate(persons):
            self._table.setItem(row, 0, QTableWidgetItem(person.label))
            for col, ev in enumerate(subject_events, start=1):
                attendances = self._attendance_service.get_event_attendance(ev.event_id)
                present = any(a.person_id == person.person_id and a.status == AttendanceStatus.PRESENT for a in attendances)
                mark = "•" if present else "—"
                item = QTableWidgetItem(mark)
                item.setTextAlignment(Qt.AlignCenter)
                if present:
                    item.setForeground(QColor("#27ae60"))
                else:
                    item.setForeground(QColor("#e74c3c"))
                self._table.setItem(row, col, item)

        self._info_label.setText(f"Показано {len(subject_events)} занятий")

    def refresh(self):
        if self._current_event:
            self.load_history(all_dates=True)