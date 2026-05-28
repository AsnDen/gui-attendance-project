from datetime import datetime, timedelta
from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QCalendarWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QMessageBox
)

from roll.core import BaseEvent
from roll.services import EventService
from roll.ui.dialogs import AddToScheduleDialog, EditEventDialog
from roll.view_models import CalendarPanelViewModel


class CalendarPanel(QFrame):
    date_selected = Signal(str)
    event_selected = Signal(object)
    data_changed = Signal()

    def __init__(self, view_model: CalendarPanelViewModel,
                 event_service: EventService,
                 template_service) -> None:
        super().__init__()
        self._view_model = view_model
        self._event_service = event_service
        self._template_service = template_service
        self._view_model.setParent(self)

        self._current_date: str | None = None
        self._current_events: list[BaseEvent] = []
        self._selected_event_id: int | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        self.setMinimumWidth(350)
        self.setMaximumWidth(400)
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
                padding: 8px;
                background-color: #34495e;
                border-radius: 8px;
            }
            QCalendarWidget {
                background-color: #34495e;
                border-radius: 8px;
                color: #ecf0f1;
            }
            QCalendarWidget QTableView {
                selection-background-color: #1abc9c;
            }
            QListWidget {
                background-color: #34495e;
                border: none;
                border-radius: 8px;
                color: #ecf0f1;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #3d5a73;
            }
            QListWidget::item:selected {
                background-color: #1abc9c;
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #16a085;
                color: white;
            }
            QPushButton#delete {
                background-color: #e74c3c;
                color: white;
            }
            QPushButton#edit {
                background-color: #f39c12;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        calendar_title = QLabel("КАЛЕНДАРЬ")
        calendar_title.setObjectName("title")
        calendar_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(calendar_title)

        self._calendar = QCalendarWidget()
        self._calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        layout.addWidget(self._calendar)

        schedule_title = QLabel("РАСПИСАНИЕ НА ДЕНЬ")
        schedule_title.setObjectName("title")
        schedule_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(schedule_title)

        self._schedule_list = QListWidget()
        self._schedule_list.itemClicked.connect(self._on_schedule_item_clicked)
        layout.addWidget(self._schedule_list)

        btn_layout = QHBoxLayout()
        self._edit_btn = QPushButton("Редактировать")
        self._edit_btn.setObjectName("edit")
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._edit_selected_event)

        self._delete_btn = QPushButton("Удалить из расписания")
        self._delete_btn.setObjectName("delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._delete_selected_event)
        btn_layout.addWidget(self._edit_btn)
        btn_layout.addWidget(self._delete_btn)
        layout.addLayout(btn_layout)

        self._add_btn = QPushButton("Добавить предмет в расписание")
        self._add_btn.clicked.connect(self._add_to_schedule)
        layout.addWidget(self._add_btn)

        self._calendar.clicked.connect(self._on_date_clicked)

    def _connect_signals(self) -> None:
        self._view_model.date_changed.connect(self._on_view_model_date_changed)
        self._view_model.event_changed.connect(self._on_view_model_events_changed)
        self._view_model.show_warning.connect(lambda msg: QMessageBox.warning(self, "Ошибка", msg))

    def _on_view_model_date_changed(self, date_str: str) -> None:
        self.date_selected.emit(date_str)

    def _on_view_model_events_changed(self, events: list[BaseEvent]) -> None:
        self._current_events = events
        self._update_schedule_list()

    def _on_date_clicked(self, date: QDate) -> None:
        self._view_model.select_date(date)
        self._view_model.load_events()

    def _update_schedule_list(self) -> None:
        self._schedule_list.clear()
        for ev in self._current_events:
            duration_min = ev.duration.seconds // 60
            display = f"{ev.label}\n   {ev.start_time.strftime('%H:%M')} ({duration_min} мин)"
            if ev.description:
                display += f"\n   {ev.description}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, ev.event_id)
            self._schedule_list.addItem(item)
        self._selected_event_id = None
        self._edit_btn.setEnabled(False)
        self._delete_btn.setEnabled(False)

    def _on_schedule_item_clicked(self, item: QListWidgetItem) -> None:
        event_id = item.data(Qt.UserRole)
        self._selected_event_id = event_id
        selected = next((e for e in self._current_events if e.event_id == event_id), None)
        if selected:
            self.event_selected.emit(selected)
            self._edit_btn.setEnabled(True)
            self._delete_btn.setEnabled(True)

    def _edit_selected_event(self):
        if self._selected_event_id is None:
            return
        event = next((e for e in self._current_events if e.event_id == self._selected_event_id), None)
        if not event:
            return
        dialog = EditEventDialog(self, event, self._template_service)
        if dialog.exec():
            new_label, new_topic, new_qtime, new_duration_min = dialog.get_data()
            from datetime import time as datetime_time
            new_time = datetime_time(new_qtime.hour(), new_qtime.minute())
            new_start = datetime.combine(event.start_time.date(), new_time)
            new_duration = timedelta(minutes=new_duration_min)
            try:
                self._view_model._event_service.update_event(
                    event.event_id,
                    label=new_label,
                    description=new_topic,
                    start_time=new_start,
                    duration=new_duration
                )
                self._view_model.load_events()
                self.data_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def _delete_selected_event(self):
        if self._selected_event_id is None:
            return
        event = next((e for e in self._current_events if e.event_id == self._selected_event_id), None)
        if not event:
            return
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить '{event.label}' с {self._current_date}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._view_model.delete_event(event.event_id, event.label, self._current_date)
            self.data_changed.emit()

    def _add_to_schedule(self) -> None:
        selected_date = self._calendar.selectedDate()
        if not selected_date:
            QMessageBox.warning(self, "Ошибка", "Выберите дату в календаре!")
            return
        date_str = selected_date.toString("yyyy-MM-dd")
        self._current_date = date_str

        templates = self._template_service.get_all_templates()
        if not templates:
            QMessageBox.warning(self, "Ошибка",
                "Нет добавленных предметов. Сначала добавьте предмет через меню 'Предметы' → 'Список предметов'.")
            return
        subjects = [(t.event_id, t.label) for t in templates]
        dialog = AddToScheduleDialog(self, date_str, subjects)
        if dialog.exec():
            subject_id, subject_label, topic, qtime, duration_min = dialog.get_data()
            from datetime import time as datetime_time
            start_time = datetime_time(qtime.hour(), qtime.minute())
            duration = timedelta(minutes=duration_min)
            self._view_model.add_new_event(
                label=subject_label,
                description=topic,
                start_time=start_time,
                duration=duration
            )
            self.data_changed.emit()

    def set_current_date(self, date_str: str) -> None:
        year, month, day = map(int, date_str.split("-"))
        date_q = QDate(year, month, day)
        self._calendar.setSelectedDate(date_q)
        self._current_date = date_str
        self._view_model.select_date(date_q)
        self._view_model.load_events()