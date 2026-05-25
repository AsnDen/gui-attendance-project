from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QVBoxLayout,
)


class DayEventsPanel(QFrame):
    event_selected: Signal = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._current_date = None
        self._current_schedule_item = None
        self._setup_ui()

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
        # self._subjects_list.itemClicked.connect(self._on_subject_click)
        # self._subjects_list.itemDoubleClicked.connect(self._open_attendance)
        layout.addWidget(self._subjects_list)

        btn_layout = QHBoxLayout()
        self._edit_btn: QPushButton = QPushButton("✏️ Ред.")
        self._edit_btn.setObjectName("edit")
        self._edit_btn.setEnabled(False)
        # self._edit_btn.clicked.connect(self._edit_subject)

        self._delete_btn: QPushButton = QPushButton("🗑️ Удалить")
        self._delete_btn.setObjectName("delete")
        self._delete_btn.setEnabled(False)
        # self._delete_btn.clicked.connect(self._delete_subject)

        btn_layout.addWidget(self._edit_btn)
        btn_layout.addWidget(self._delete_btn)
        layout.addLayout(btn_layout)

        self._attendance_btn: QPushButton = QPushButton("📋 Отметить посещаемость")
        self._attendance_btn.setObjectName("attendance")
        self._attendance_btn.setEnabled(False)
        # self._attendance_btn.clicked.connect(self._open_attendance)
        layout.addWidget(self._attendance_btn)

        self._selected_label: QLabel = QLabel("⚡ Выберите предмет")
        self._selected_label.setStyleSheet("color: #1abc9c; font-size: 11px;")
        self._selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._selected_label)

    def set_date(self, date: str) -> None:
        self._current_date = date
        self._date_label.setText(f"📅 {date}")
        # self._load_subjects()
        self._current_schedule_item = None
        self._selected_label.setText("⚡ Выберите предмет")
        self._edit_btn.setEnabled(False)
        self._delete_btn.setEnabled(False)
        self._attendance_btn.setEnabled(False)

    #
    # def _load_subjects(self) -> None:
    #     self._subjects_list.clear()
    #     if not self._current_date:
    #         return
    #
    #     items = self._db.get_schedule_for_date(self._current_date)
    #     for item in items:
    #         display_text = f"📖 {item.subject_name}"
    #         if item.topic:
    #             display_text += f"\n   └ {item.topic}"
    #         display_text += f"\n   👥 Присутствует: {len(item.member_ids)} чел."
    #
    #         list_item = QListWidgetItem(display_text)
    #         list_item.setData(Qt.UserRole, item.id)
    #         self._subjects_list.addItem(list_item)
    #
    # def _on_subject_click(self, item) -> None:
    #     item_id = item.data(Qt.UserRole)
    #     items = self._db.get_schedule_for_date(self._current_date)
    #     self._current_schedule_item = next((i for i in items if i.id == item_id), None)
    #     if self._current_schedule_item:
    #         self._selected_label.setText(
    #             f"✅ ВЫБРАН: {self._current_schedule_item.subject_name}"
    #         )
    #         self._edit_btn.setEnabled(True)
    #         self._delete_btn.setEnabled(True)
    #         self._attendance_btn.setEnabled(True)
    #         self.subject_selected.emit(self._current_schedule_item)
    #
    # def _edit_subject(self) -> None:
    #     if self._current_schedule_item:
    #         dialog = EditScheduleDialog(self, self._current_schedule_item)
    #         if dialog.exec():
    #             new_name, new_topic = dialog.get_data()
    #             if new_name:
    #                 self._current_schedule_item.subject_name = new_name
    #                 self._current_schedule_item.topic = new_topic
    #                 self._db.update_schedule_item(self._current_schedule_item)
    #                 self._load_subjects()
    #                 QMessageBox.information(self, "Успех", "Предмет обновлён!")
    #
    # def _delete_subject(self) -> None:
    #     if (
    #         self._current_schedule_item
    #         and QMessageBox.question(
    #             self,
    #             "Подтверждение",
    #             f"Удалить '{self._current_schedule_item.subject_name}'?",
    #         )
    #         == QMessageBox.Yes
    #     ):
    #         self._db.delete_schedule_item(self._current_schedule_item.id)
    #         self._current_schedule_item = None
    #         self._load_subjects()
    #         self._selected_label.setText("⚡ Выберите предмет")
    #         self._edit_btn.setEnabled(False)
    #         self._delete_btn.setEnabled(False)
    #         self._attendance_btn.setEnabled(False)
    #
    # def _open_attendance(self) -> None:
    #     if self._current_schedule_item:
    #         dialog = AttendanceDialog(self, self._db, self._current_schedule_item)
    #         dialog.exec()
    #         self._load_subjects()
    #
    # def get_current_item(self) -> None:
    #     return self._current_schedule_item
    #
    # def refresh(self) -> None:
    #     self._load_subjects()
