from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QCheckBox, QMessageBox, QDialog
)
from .base import BaseDialog
from roll.core import AttendanceStatus


class AttendanceDialog(BaseDialog):
    data_changed = Signal()

    def __init__(self, parent, attendance_service, person_service, event):
        super().__init__(parent)
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._event = event
        self.setWindowTitle(f"Посещаемость: {event.label} - {event.start_time.date()}")
        self.setModal(True)
        self.setMinimumSize(500, 500)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        title = QLabel("ПОСЕЩАЕМОСТЬ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)

        info_text = f"{self._event.label}\n{self._event.description or ''}\n{self._event.start_time.date()}"
        info_label = QLabel(info_text)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        btn_layout = QHBoxLayout()
        all_btn = QPushButton("Отметить всех")
        all_btn.clicked.connect(self._mark_all)
        clear_btn = QPushButton("Снять всех")
        clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(all_btn)
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Участник", "Статус"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setColumnWidth(0, 250)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._table)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_data(self):
        persons = self._person_service.get_all_persons()
        attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._event.event_id)}
        self._table.setRowCount(len(persons))
        self._person_map = {}
        for row, person in enumerate(persons):
            self._person_map[row] = person.person_id
            self._table.setItem(row, 0, QTableWidgetItem(person.label))
            status = attendances.get(person.person_id)
            is_present = status is not None and status.status == AttendanceStatus.PRESENT
            status_text = "ПРИСУТСТВУЕТ" if is_present else "ОТСУТСТВУЕТ"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#27ae60") if is_present else QColor("#e74c3c"))
            self._table.setItem(row, 1, status_item)

    def _on_item_double_clicked(self, item):
        row = item.row()
        person_id = self._person_map.get(row)
        if person_id:
            self._toggle_member(person_id)

    def _toggle_member(self, person_id):
        attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._event.event_id)}
        existing = attendances.get(person_id)
        if existing and existing.status == AttendanceStatus.PRESENT:
            self._attendance_service.update_attendance(existing.attendance_id, AttendanceStatus.ABSENT)
        else:
            self._attendance_service.add_attendance(person_id, self._event.event_id, AttendanceStatus.PRESENT)
        self._load_data()
        self.data_changed.emit()

    def _mark_all(self):
        persons = self._person_service.get_all_persons()
        for person in persons:
            att_list = self._attendance_service.get_event_attendance(self._event.event_id)
            existing = next((a for a in att_list if a.person_id == person.person_id), None)
            if existing:
                if existing.status != AttendanceStatus.PRESENT:
                    self._attendance_service.update_attendance(existing.attendance_id, AttendanceStatus.PRESENT)
            else:
                self._attendance_service.add_attendance(person.person_id, self._event.event_id, AttendanceStatus.PRESENT)
        self._load_data()
        self.data_changed.emit()

    def _clear_all(self):
        for a in self._attendance_service.get_event_attendance(self._event.event_id):
            if a.status == AttendanceStatus.PRESENT:
                self._attendance_service.update_attendance(a.attendance_id, AttendanceStatus.ABSENT)
        self._load_data()
        self.data_changed.emit()


class ManualAttendanceDialog(BaseDialog):
    def __init__(self, parent, person_service, attendance_service, event):
        super().__init__(parent)
        self._person_service = person_service
        self._attendance_service = attendance_service
        self._event = event
        self.setWindowTitle(f"Ручная отметка - {event.label}")
        self.setModal(True)
        self.setMinimumSize(400, 500)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Участник", "Присутствует"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self._load_persons()

    def _load_persons(self):
        persons = list(self._person_service.get_all_persons())
        persons.sort(key=lambda p: p.label.lower())
        self._table.setRowCount(len(persons))
        self._person_ids = []
        self._checkboxes = []

        attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._event.event_id)}

        for row, person in enumerate(persons):
            self._table.setItem(row, 0, QTableWidgetItem(person.label))
            self._person_ids.append(person.person_id)
            cb = QCheckBox()
            is_present = person.person_id in attendances and attendances[person.person_id].status == AttendanceStatus.PRESENT
            cb.setChecked(is_present)
            self._table.setCellWidget(row, 1, cb)
            self._checkboxes.append(cb)

    def _save(self):
        changed = 0
        for idx, person_id in enumerate(self._person_ids):
            cb = self._checkboxes[idx]
            is_present = cb.isChecked()
            attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._event.event_id)}
            existing = attendances.get(person_id)
            if is_present:
                if not existing or existing.status != AttendanceStatus.PRESENT:
                    if existing:
                        self._attendance_service.update_attendance(existing.attendance_id, AttendanceStatus.PRESENT)
                    else:
                        self._attendance_service.add_attendance(person_id, self._event.event_id, AttendanceStatus.PRESENT)
                    changed += 1
            else:
                if existing and existing.status == AttendanceStatus.PRESENT:
                    self._attendance_service.update_attendance(existing.attendance_id, AttendanceStatus.ABSENT)
                    changed += 1
        if changed:
            QMessageBox.information(self, "Успех", f"Обновлено {changed} записей.")
        self.accept()


class AttendanceDetailsDialog(BaseDialog):
    def __init__(self, parent, attendance_service, person_service, event):
        super().__init__(parent)
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._event = event
        self.setWindowTitle(f"Отметившиеся на {event.label} ({event.start_time.date()})")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("СПИСОК ОТМЕТИВШИХСЯ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)
        self._table = QTableWidget()
        self._table.setColumnCount(1)
        self._table.setHorizontalHeaderLabels(["Участник"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_data(self):
        attendances = self._attendance_service.get_event_attendance(self._event.event_id)
        present = [a for a in attendances if a.status == AttendanceStatus.PRESENT]
        self._table.setRowCount(len(present))
        for row, a in enumerate(present):
            person = self._person_service.get_person(a.person_id)
            name = person.label if person else f"ID {a.person_id}"
            self._table.setItem(row, 0, QTableWidgetItem(name))