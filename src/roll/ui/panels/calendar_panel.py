from datetime import time as dt_time
from datetime import timedelta
from typing import cast

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from roll.core import EventTemplate
from roll.view_models import CalendarPanelViewModel


class CalendarPanel(QFrame):
    date_selected: Signal = Signal(str)

    def __init__(self, view_model: CalendarPanelViewModel) -> None:
        super().__init__()
        self._view_model: CalendarPanelViewModel = view_model

        self._view_model.setParent(self)
        self._setup_ui()
        self._connect_signals()

        self._view_model.load_event_templates()
        self._view_model.load_events()

    def _setup_ui(self) -> None:
        self.setMinimumWidth(350)
        self.setMaximumWidth(400)
        self.setStyleSheet("""
            QFrame { background-color: #2c3e50; border-radius: 12px; margin: 5px; }
            QLabel#title { color: #ecf0f1; font-size: 16px; font-weight: bold; padding: 8px; background-color: #34495e; border-radius: 8px; }
            QCalendarWidget { background-color: #34495e; border-radius: 8px; color: #ecf0f1; }
            QCalendarWidget QTableView { selection-background-color: #1abc9c; }
            QListWidget { background-color: #34495e; border: none; border-radius: 8px; color: #ecf0f1; font-size: 12px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #3d5a73; }
            QPushButton { background-color: #1abc9c; border: none; border-radius: 6px; padding: 8px; color: #2c3e50; font-weight: bold; }
            QPushButton:hover { background-color: #16a085; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        calendar_title = QLabel("📅 КАЛЕНДАРЬ")
        calendar_title.setObjectName("title")
        calendar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(calendar_title)

        self._calendar: QCalendarWidget = QCalendarWidget()
        self._calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        layout.addWidget(self._calendar)

        # all events as a list
        subjects_title = QLabel("📋 ВСЕ ПРЕДМЕТЫ В РАСПИСАНИИ")
        subjects_title.setObjectName("title")
        subjects_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subjects_title)

        self._all_subjects_list: QListWidget = QListWidget()
        layout.addWidget(self._all_subjects_list)

        add_btn = QPushButton("➕ Добавить предмет на выбранную дату")
        layout.addWidget(add_btn)

        _ = self._calendar.clicked.connect(self._on_date_clicked)
        _ = self._all_subjects_list.itemDoubleClicked.connect(
            self._on_template_double_clicked
        )
        _ = add_btn.clicked.connect(self._on_add_event_clicked)

    def _connect_signals(self) -> None:
        _ = self._view_model.template_changed.connect(self._on_templates_loaded)
        _ = self._view_model.show_warning.connect(self._display_warning)
        _ = self._view_model.show_success.connect(self._display_success)
        _ = self._view_model.date_changed.connect(self._on_view_model_date_changed)

    def _on_templates_loaded(self, templates: list[EventTemplate]) -> None:
        self._all_subjects_list.clear()
        for template in templates:
            list_item = QListWidgetItem(f"📖 {template.label}")
            list_item.setData(Qt.ItemDataRole.UserRole, template)
            self._all_subjects_list.addItem(list_item)

    def _on_view_model_date_changed(self, date_str: str) -> None:
        self.date_selected.emit(date_str)

    def _display_warning(self, message: str) -> None:
        _ = QMessageBox.warning(self, "Предупреждение", message)

    def _display_success(self, message: str) -> None:
        _ = QMessageBox.information(self, "Успех", message)

    def _on_date_clicked(self, date: QDate) -> None:
        self._view_model.select_date(date)
        self._view_model.load_events()

    def _on_template_double_clicked(self, item: QListWidgetItem) -> None:
        template: EventTemplate = cast(
            "EventTemplate", item.data(Qt.ItemDataRole.UserRole)
        )
        if template:
            self._view_model.quick_add_template(template)

    def _on_add_event_clicked(self) -> None:
        name: str
        ok: bool
        name, ok = QInputDialog.getText(self, "Новый предмет", "Название предмета:")
        if not ok or not name.strip():
            return

        self._view_model.add_new_template(
            label=name.strip(),
            description="",
            start_time=dt_time(9, 0),
            duration=timedelta(hours=1, minutes=30),
        )

    def set_current_date(self, date_str: str) -> None:
        year, month, day = map(int, date_str.split("-"))
        self._calendar.setSelectedDate(QDate(year, month, day))
        self._view_model.select_date(QDate(year, month, day))
