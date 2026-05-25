from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCalendarWidget,
    QFrame,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)


class CalendarPanel(QFrame):
    date_selected: Signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

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
        # _ = self._calendar.clicked.connect(self._on_date_clicked)
        layout.addWidget(self._calendar)

        # all events as a list
        subjects_title = QLabel("📋 ВСЕ ПРЕДМЕТЫ В РАСПИСАНИИ")
        subjects_title.setObjectName("title")
        subjects_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subjects_title)

        self._all_subjects_list: QListWidget = QListWidget()
        # _ = self._all_subjects_list.itemDoubleClicked.connect(self._quick_add_to_date)
        layout.addWidget(self._all_subjects_list)

        # self._load_all_subjects()

        add_btn = QPushButton("➕ Добавить предмет на выбранную дату")
        # _ = add_btn.clicked.connect(self._add_to_selected_date)
        layout.addWidget(add_btn)

    # def _on_date_clicked(self, date: QDate) -> None:
    #     date_str = date.toString("yyyy-MM-dd")
    #     self.date_selected.emit(date_str)
    #
    # def _load_all_subjects(self) -> None:
    #     # self._all_subjects_list.clear()
    #     # schedule = self._db.get_schedule()
    #     # unique_subjects = {}
    #     # for item in schedule:
    #     #     if item.subject_name not in unique_subjects:
    #     #         unique_subjects[item.subject_name] = item.id
    #     #         list_item = QListWidgetItem(f"📖 {item.subject_name}")
    #     #         list_item.setData(Qt.UserRole, item.subject_name)
    #     #         self._all_subjects_list.addItem(list_item)
    #     pass
    #
    # def _add_to_selected_date(self) -> None:
    #     # selected = self._calendar.selectedDate()
    #     # if not selected:
    #     #     _ = QMessageBox.warning(self, "Ошибка", "Выберите дату в календаре!")
    #     #     return
    #     #
    #     # date_str = selected.toString("yyyy-MM-dd")
    #     #
    #     # name, ok = QInputDialog.getText(self, "Новый предмет", "Название предмета:")
    #     # if not ok or not name:
    #     #     return
    #     #
    #     # topic, ok = QInputDialog.getText(self, "Тема занятия", f"Тема для '{name}':")
    #     # if not ok:
    #     #     topic = ""
    #     #
    #     # schedule = self._db.get_schedule()
    #     # new_id = max([s.id for s in schedule], default=0) + 1
    #     # new_item = ScheduleItem(
    #     #     id=new_id, subject_name=name, topic=topic, date=date_str, member_ids=[]
    #     # )
    #     # self._db.add_schedule_item(new_item)
    #     #
    #     # self._load_all_subjects()
    #     # self.date_selected.emit(date_str)
    #     # QMessageBox.information(
    #     #     self, "Успех", f"Предмет '{name}' добавлен на {date_str}"
    #     # )
    #     pass
    #
    # def _quick_add_to_date(self, item) -> None:
    #     subject_name = item.data(Qt.ItemDataRole.UserRole)
    #     selected = self._calendar.selectedDate()
    #     if not selected:
    #         _ = QMessageBox.warning(self, "Ошибка", "Выберите дату в календаре!")
    #         return
    #
    #     date_str = selected.toString("yyyy-MM-dd")
    #
    #     existing = self._db.get_schedule_for_date(date_str)
    #     if any(s.subject_name == subject_name for s in existing):
    #         QMessageBox.warning(
    #             self, "Ошибка", f"Предмет '{subject_name}' уже есть на {date_str}!"
    #         )
    #         return
    #
    #     topic, ok = QInputDialog.getText(
    #         self, "Тема занятия", f"Тема для '{subject_name}':"
    #     )
    #     if not ok:
    #         topic = ""
    #
    #     schedule = self._db.get_schedule()
    #     new_id = max([s.id for s in schedule], default=0) + 1
    #     new_item = ScheduleItem(
    #         id=new_id,
    #         subject_name=subject_name,
    #         topic=topic,
    #         date=date_str,
    #         member_ids=[],
    #     )
    #     self._db.add_schedule_item(new_item)
    #
    #     self.date_selected.emit(date_str)
    #     QMessageBox.information(
    #         self, "Успех", f"Предмет '{subject_name}' добавлен на {date_str}"
    #     )
    #
    # def set_current_date(self, date_str: str) -> None:
    #     year, month, day = map(int, date_str.split("-"))
    #     self._calendar.setSelectedDate(QDate(year, month, day))
