from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from roll.core import BaseEvent


class DayEventsPanel(QFrame):
    event_selected = Signal(object)  # передаёт BaseEvent

    def __init__(self) -> None:
        super().__init__()
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
            QPushButton { background-color: #1abc9c; border: none; border-radius: 6px; padding: 8px; color: #2c3e50; font-weight: bold; }
            QPushButton:hover { background-color: #16a085; color: white; }
            QPushButton#delete { background-color: #e74c3c; color: white; }
            QPushButton#edit { background-color: #f39c12; color: white; }
            QPushButton#attendance { background-color: #9b59b6; color: white; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        self._date_label: QLabel = QLabel("📅 ВЫБЕРИТЕ ДЕНЬ")
        self._date_label.setObjectName("title")
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._date_label)

        self._subjects_list: QListWidget = QListWidget()
        layout.addWidget(self._subjects_list)

        btn_layout = QHBoxLayout()
        self._edit_btn: QPushButton = QPushButton("✏️ Ред.")
        self._edit_btn.setObjectName("edit")
        self._edit_btn.setEnabled(False)

        self._delete_btn: QPushButton = QPushButton("🗑️ Удалить")
        self._delete_btn.setObjectName("delete")
        self._delete_btn.setEnabled(False)

        btn_layout.addWidget(self._edit_btn)
        btn_layout.addWidget(self._delete_btn)
        layout.addLayout(btn_layout)

        self._attendance_btn: QPushButton = QPushButton("📋 Отметить посещаемость")
        self._attendance_btn.setObjectName("attendance")
        self._attendance_btn.setEnabled(False)
        layout.addWidget(self._attendance_btn)

        self._selected_label: QLabel = QLabel("⚡ Выберите предмет")
        self._selected_label.setStyleSheet("color: #1abc9c; font-size: 11px;")
        self._selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._selected_label)

    def _connect_signals(self) -> None:
        self._subjects_list.itemClicked.connect(self._on_item_clicked)

    def set_date(self, date: str) -> None:
        self._current_date = date
        self._date_label.setText(f"📅 {date}")
        self._selected_event = None
        self._update_selection_ui()

    def set_events(self, events: list[BaseEvent]) -> None:
        self._current_events = events
        self._subjects_list.clear()
        for ev in events:
            display = f"📖 {ev.label}\n   🕒 {ev.start_time.strftime('%H:%M')} ({ev.duration.seconds // 60} мин)"
            if ev.description:
                display += f"\n   📝 {ev.description}"
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

    def _update_selection_ui(self) -> None:
        enabled = self._selected_event is not None
        self._edit_btn.setEnabled(enabled)
        self._delete_btn.setEnabled(enabled)
        self._attendance_btn.setEnabled(enabled)
        if self._selected_event:
            self._selected_label.setText(f"✅ ВЫБРАН: {self._selected_event.label}")
        else:
            self._selected_label.setText("⚡ Выберите предмет")

    def get_current_event(self) -> BaseEvent | None:
        return self._selected_event

    def refresh(self) -> None:
        # Метод для обновления списка (может быть вызван извне)
        pass