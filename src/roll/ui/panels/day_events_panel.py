# src/roll/ui/panels/day_events_panel.py
from datetime import date
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout
)

from roll.core import BaseEvent
from roll.ui.dialogs import EditEventDialog, AttendanceDetailsDialog
from roll.view_models.day_events_viewmodel import DayEventsViewModel


class DayEventsPanel(QFrame):
    event_selected = Signal(object)

    def __init__(self, view_model: DayEventsViewModel) -> None:
        super().__init__()
        self._view_model = view_model
        self._view_model.setParent(self)

        self._current_date: str | None = None
        self._current_events: list[BaseEvent] = []
        self._selected_event: BaseEvent | None = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        self.setMinimumWidth(300)
        self.setMaximumWidth(350)
        self.setStyleSheet("""
            QFrame { background-color: #2c3e50; border-radius: 12px; margin: 5px; }
            QLabel#title { color: #ecf0f1; font-size: 16px; font-weight: bold; padding: 10px; background-color: #34495e; border-radius: 8px; }
            QListWidget { background-color: #34495e; border: none; border-radius: 8px; color: #ecf0f1; font-size: 13px; outline: none; }
            QListWidget::item { padding: 12px; border-bottom: 1px solid #3d5a73; }
            QListWidget::item:selected { background-color: #1abc9c; color: #2c3e50; font-weight: bold; }
            QPushButton { background-color: #1abc9c; border: none; border-radius: 6px; padding: 10px; color: #2c3e50; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #16a085; color: white; }
            QPushButton#delete { background-color: #e74c3c; color: white; }
            QPushButton#edit { background-color: #f39c12; color: white; }
            QPushButton#attendance { background-color: #9b59b6; color: white; }
            QPushButton#delete_subject { background-color: #c0392b; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        self._date_label = QLabel("ВЫБЕРИТЕ ДЕНЬ")
        self._date_label.setObjectName("title")
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._date_label)

        self._subjects_list = QListWidget()
        layout.addWidget(self._subjects_list)

        btn_layout1 = QHBoxLayout()
        self._edit_btn = QPushButton("Ред.")
        self._edit_btn.setObjectName("edit")
        self._edit_btn.setEnabled(False)

        self._delete_from_schedule_btn = QPushButton("Удалить из расписания")
        self._delete_from_schedule_btn.setObjectName("delete")
        self._delete_from_schedule_btn.setEnabled(False)
        btn_layout1.addWidget(self._edit_btn)
        btn_layout1.addWidget(self._delete_from_schedule_btn)
        layout.addLayout(btn_layout1)

        btn_layout2 = QHBoxLayout()
        self._attendance_btn = QPushButton("Отметить посещаемость")
        self._attendance_btn.setObjectName("attendance")
        self._attendance_btn.setEnabled(False)

        self._delete_subject_btn = QPushButton("Удалить предмет полностью")
        self._delete_subject_btn.setObjectName("delete_subject")
        self._delete_subject_btn.setEnabled(False)
        btn_layout2.addWidget(self._attendance_btn)
        btn_layout2.addWidget(self._delete_subject_btn)
        layout.addLayout(btn_layout2)

        self._selected_label = QLabel("Выберите предмет")
        self._selected_label.setStyleSheet("color: #1abc9c; font-size: 11px;")
        self._selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._selected_label)

    def _connect_signals(self) -> None:
        self._subjects_list.itemClicked.connect(self._on_item_clicked)
        self._edit_btn.clicked.connect(self._edit_event)
        self._delete_from_schedule_btn.clicked.connect(self._delete_from_schedule)
        self._attendance_btn.clicked.connect(self._open_attendance)
        self._delete_subject_btn.clicked.connect(self._delete_subject_completely)
        self._view_model.data_changed.connect(self.refresh)

    def set_date(self, date_str: str) -> None:
        self._current_date = date_str
        self._date_label.setText(date_str)
        self._selected_event = None
        self._update_selection_ui()
        self.refresh()

    def refresh(self) -> None:
        if self._current_date:
            events = self._view_model.get_day_events(self._current_date)
            self._set_events(list(events))

    def _set_events(self, events: list[BaseEvent]) -> None:
        self._current_events = events
        self._subjects_list.clear()
        for ev in events:
            present_count = self._view_model.get_attendance_count(ev.event_id)
            display = f"{ev.label}\n   {ev.start_time.strftime('%H:%M')} ({ev.duration.seconds // 60} мин)"
            if ev.description:
                display += f"\n   {ev.description}"
            display += f"\n   Присутствует: {present_count} чел."
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, ev.event_id)
            self._subjects_list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        event_id = item.data(Qt.UserRole)
        self._selected_event = next(
            (e for e in self._current_events if e.event_id == event_id), None
        )
        self._update_selection_ui()
        if self._selected_event:
            self.event_selected.emit(self._selected_event)
            self._show_attendance_details()

    def _show_attendance_details(self):
        if self._selected_event:
            from roll.ui.dialogs import AttendanceDetailsDialog
            dialog = AttendanceDetailsDialog(
                self,
                self._view_model._attendance_service,   # можно передать, если нужно – но лучше через ViewModel, оставим как есть для краткости
                self._view_model._person_service,
                self._selected_event
            )
            dialog.exec()

    def _update_selection_ui(self) -> None:
        enabled = self._selected_event is not None
        self._edit_btn.setEnabled(enabled)
        self._delete_from_schedule_btn.setEnabled(enabled)
        self._attendance_btn.setEnabled(enabled)
        self._delete_subject_btn.setEnabled(enabled)
        if self._selected_event:
            self._selected_label.setText(f"ВЫБРАН: {self._selected_event.label}")
        else:
            self._selected_label.setText("Выберите предмет")

    def _edit_event(self) -> None:
        if not self._selected_event:
            return
        from roll.ui.dialogs import EditEventDialog
        # Для редактирования нужен template_service, но его нет в ViewModel.
        # Временно передадим через родительский виджет (в MainWindow) – но это костыль.
        # Лучше добавить в ViewModel метод для получения шаблонов, но для простоты оставим как есть.
        # (В реальном рефакторинге EditEventDialog тоже должен использовать ViewModel)
        # Для совместимости передадим template_service из MainWindow, но пока заглушка:
        template_service = getattr(self.parent(), '_template_service', None)
        if template_service is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить список предметов.")
            return
        dialog = EditEventDialog(self, self._selected_event, template_service)
        if dialog.exec():
            new_label, new_topic = dialog.get_data()
            if new_label:
                self._view_model.update_event(self._selected_event.event_id, new_label, new_topic)
                # После обновления сигнал data_changed вызовет refresh
                self.event_selected.emit(self._selected_event)

    def _delete_from_schedule(self) -> None:
        if not self._selected_event:
            return
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить '{self._selected_event.label}' с {self._current_date}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._view_model.delete_event(self._selected_event.event_id, self._selected_event.label)
            self._selected_event = None

    def _delete_subject_completely(self) -> None:
        if not self._selected_event:
            return
        subject_name = self._selected_event.label
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить ВСЕ занятия по предмету '{subject_name}'?\nЭто действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._view_model.delete_all_events_by_label(subject_name)
            self._selected_event = None
            self.event_selected.emit(None)

    def _open_attendance(self) -> None:
        if not self._selected_event:
            return
        self._view_model.open_attendance_dialog(self._selected_event, self)
        # После закрытия диалога data_changed обновит список

    def get_current_event(self) -> BaseEvent | None:
        return self._selected_event
