from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QComboBox, QTimeEdit, QSpinBox, QDialog
)
from .base import BaseDialog
from roll.core import BaseEvent


class AddToScheduleDialog(BaseDialog):
    def __init__(self, parent, date_str: str, subjects: list[tuple]):
        super().__init__(parent)
        self._date_str = date_str
        self._subjects = sorted(subjects, key=lambda x: x[1])
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"Добавить предмет на {self._date_str}")
        self.setModal(True)
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        title = QLabel("ДОБАВЛЕНИЕ ПРЕДМЕТА В РАСПИСАНИЕ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        date_label = QLabel(f"Дата: {self._date_str}")
        date_label.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(date_label)
        form = QFormLayout()
        self._subject_combo = QComboBox()
        for subj_id, subj_name in self._subjects:
            self._subject_combo.addItem(subj_name, subj_id)
        self._subject_combo.setEditable(False)
        form.addRow("Предмет:", self._subject_combo)
        self._topic_edit = QLineEdit()
        self._topic_edit.setPlaceholderText("Тема занятия (необязательно)")
        form.addRow("Тема:", self._topic_edit)
        self._time_edit = QTimeEdit()
        self._time_edit.setTime(QTime(9, 0))
        self._time_edit.setDisplayFormat("HH:mm")
        form.addRow("Время начала:", self._time_edit)
        self._duration_edit = QSpinBox()
        self._duration_edit.setRange(5, 600)
        self._duration_edit.setValue(90)
        self._duration_edit.setSuffix(" мин")
        form.addRow("Длительность:", self._duration_edit)
        layout.addLayout(form)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Добавить в расписание")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return (
            self._subject_combo.currentData(),
            self._subject_combo.currentText(),
            self._topic_edit.text().strip(),
            self._time_edit.time(),
            self._duration_edit.value(),
        )


class EditEventDialog(BaseDialog):
    def __init__(self, parent, event: BaseEvent, template_service):
        super().__init__(parent)
        self._event = event
        self._template_service = template_service
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("Редактировать событие")
        self.setModal(True)
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        title = QLabel("РЕДАКТИРОВАНИЕ СОБЫТИЯ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #f39c12;")
        layout.addWidget(title)

        form = QFormLayout()
        self._name_combo = QComboBox()
        templates = list(self._template_service.get_all_templates())
        templates.sort(key=lambda t: t.label.lower())
        for t in templates:
            self._name_combo.addItem(t.label, t.event_id)
        self._name_combo.setEditable(False)
        form.addRow("Предмет:", self._name_combo)

        self._topic_edit = QLineEdit()
        form.addRow("Тема:", self._topic_edit)

        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        form.addRow("Время начала:", self._time_edit)

        self._duration_edit = QSpinBox()
        self._duration_edit.setRange(5, 600)
        self._duration_edit.setSuffix(" мин")
        form.addRow("Длительность (мин):", self._duration_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _load_data(self):
        index = self._name_combo.findText(self._event.label)
        if index >= 0:
            self._name_combo.setCurrentIndex(index)
        self._topic_edit.setText(self._event.description or "")
        self._time_edit.setTime(self._event.start_time.time())
        self._duration_edit.setValue(self._event.duration.seconds // 60)

    def get_data(self):
        return (
            self._name_combo.currentText(),
            self._topic_edit.text().strip(),
            self._time_edit.time(),
            self._duration_edit.value()
        )