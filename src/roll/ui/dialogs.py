# src/roll/ui/dialogs.py
from datetime import datetime, time, timedelta
from PySide6.QtCore import Qt, QTime, Signal, QEventLoop
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFormLayout, QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog,
    QHeaderView, QWidget, QTimeEdit, QSpinBox, QComboBox, QFileDialog
)
from PySide6.QtCore import QTimer

from roll.core import AttendanceStatus, BaseEvent
from roll.services import AttendanceService, PersonService, IdentifierService, EventTemplateService
from roll.view_models.qr_scanner_viewmodel import QRScannerViewModel


# ---------- QRScanDialog (без изменений) ----------
class QRScanDialog(QDialog):
    def __init__(self, parent, scanner_vm):
        super().__init__(parent)
        self._scanner_vm = scanner_vm
        self._scanned_hash = None
        self._setup_ui()
        self._connect_signals()
        self._scanner_vm.start_scanning()

    def _setup_ui(self):
        self.setWindowTitle("Сканирование QR-кода")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)

        self._preview_label = QLabel()
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setFixedHeight(350)
        self._preview_label.setStyleSheet("background-color: black;")
        layout.addWidget(self._preview_label)

        self._status_label = QLabel("Наведите камеру на QR-код...")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        btn_layout = QHBoxLayout()
        self._image_btn = QPushButton("Сканировать с фото")
        self._image_btn.clicked.connect(self._load_image)
        self._camera_btn = QPushButton("Запустить камеру")
        self._camera_btn.clicked.connect(self._start_camera)
        self._stop_btn = QPushButton("Остановить")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_camera)
        btn_layout.addWidget(self._image_btn)
        btn_layout.addWidget(self._camera_btn)
        btn_layout.addWidget(self._stop_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self._scanner_vm.frame_ready.connect(self._on_frame)
        self._scanner_vm.qr_detected.connect(self._on_qr)
        self._scanner_vm.error_occurred.connect(self._on_error)
        self._scanner_vm.scan_started.connect(lambda: self._status_label.setText("Сканирование..."))
        self._scanner_vm.scan_stopped.connect(lambda: self._status_label.setText("Камера остановлена"))

    def _on_frame(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview_label.setPixmap(scaled)

    def _on_qr(self, hash_value):
        self._scanned_hash = hash_value
        self._stop_camera()
        self.accept()

    def _on_error(self, msg):
        self._status_label.setText(f"Ошибка: {msg}")

    def _load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._preview_label.setPixmap(scaled)
            self._status_label.setText("Изображение загружено, распознаю QR...")
            QTimer.singleShot(1000, lambda: self._on_qr("fake_hash_123"))

    def _start_camera(self):
        self._scanner_vm.start_scanning()
        self._camera_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def _stop_camera(self):
        self._scanner_vm.stop_scanning()
        loop = QEventLoop()
        self._scanner_vm.scan_stopped.connect(loop.quit)
        loop.exec()
        self._preview_label.clear()
        self._preview_label.setText("Камера остановлена")
        self._camera_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def reject(self):
        self._stop_camera()
        super().reject()

    def get_hash(self):
        return self._scanned_hash


# ---------- GroupManagementDialog (без изменений) ----------
class GroupManagementDialog(QDialog):
    def __init__(self, parent, person_service: PersonService,
                 identifier_service: IdentifierService):
        super().__init__(parent)
        self._person_service = person_service
        self._identifier_service = identifier_service
        self.setWindowTitle("Управление группой")
        self.setModal(True)
        self.setMinimumSize(600, 550)
        self._setup_ui()
        self._load_members()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("СПИСОК ГРУППЫ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["ID", "ФИО", "QR-код", ""])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setDefaultSectionSize(35)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_member)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete_member)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_members(self):
        persons = self._person_service.get_all_persons()
        self._table.setRowCount(len(persons))
        for row, person in enumerate(persons):
            self._table.setItem(row, 0, QTableWidgetItem(str(person.person_id)))
            name_item = QTableWidgetItem(person.label)
            name_item.setFlags(name_item.flags() | Qt.ItemIsEditable)
            self._table.setItem(row, 1, name_item)

            identifiers = self._identifier_service.get_person_identifiers(person.person_id)
            has_qr = len(identifiers) > 0
            qr_status = "Привязан" if has_qr else "Не привязан"
            qr_item = QTableWidgetItem(qr_status)
            if not has_qr:
                qr_item.setForeground(QColor("#7f8c8d"))
            self._table.setItem(row, 2, qr_item)

            btn = QPushButton("Удалить QR" if has_qr else "Привязать QR")
            if has_qr:
                btn.clicked.connect(lambda checked, pid=person.person_id: self._unbind_qr(pid))
            else:
                btn.clicked.connect(lambda checked, pid=person.person_id: self._bind_qr(pid))
            self._table.setCellWidget(row, 3, btn)

            self._table.item(row, 0).setData(Qt.UserRole, person.person_id)

        self._table.itemChanged.connect(self._on_name_changed)

    def _on_name_changed(self, item):
        if item.column() == 1:
            row = item.row()
            person_id = self._table.item(row, 0).data(Qt.UserRole)
            new_name = item.text().strip()
            if new_name:
                try:
                    self._person_service.update_person(person_id, label=new_name)
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось обновить имя: {e}")

    def _add_member(self):
        name, ok = QInputDialog.getText(self, "Новый участник", "Введите ФИО:")
        if ok and name:
            self._person_service.add_person(label=name, description="")
            self._load_members()

    def _delete_member(self):
        current_row = self._table.currentRow()
        if current_row >= 0:
            person_id = self._table.item(current_row, 0).data(Qt.UserRole)
            person = self._person_service.get_person(person_id)
            if person and QMessageBox.question(
                self, "Подтверждение", f"Удалить '{person.label}'?"
            ) == QMessageBox.Yes:
                self._person_service.delete_person(person_id)
                self._load_members()

    def _bind_qr(self, person_id):
        person = self._person_service.get_person(person_id)
        if not person:
            return
        scanner_vm = QRScannerViewModel()
        dialog = QRScanDialog(self, scanner_vm)
        if dialog.exec() == QDialog.Accepted:
            qr_hash = dialog.get_hash()
            if qr_hash:
                existing_person = self._identifier_service.find_person_by_hash(qr_hash)
                if existing_person and existing_person.person_id != person_id:
                    QMessageBox.warning(self, "Ошибка", f"QR-код уже привязан к {existing_person.label}.")
                    return
                try:
                    self._identifier_service.add_identifier(hash_value=qr_hash, person_id=person_id)
                    QMessageBox.information(self, "Успех", f"QR-код привязан к {person.label}")
                    self._load_members()
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", str(e))

    def _unbind_qr(self, person_id):
        person = self._person_service.get_person(person_id)
        if not person:
            return
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить QR-код у '{person.label}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                identifiers = self._identifier_service.get_person_identifiers(person_id)
                for ident in identifiers:
                    self._identifier_service.delete_identifier(ident.identifier_id)
                QMessageBox.information(self, "Успех", f"QR-код удалён у {person.label}")
                self._load_members()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))


# ---------- AttendanceDialog (без изменений) ----------
class AttendanceDialog(QDialog):
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
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)

        subject_label = QLabel(f"Предмет: {self._event.label}")
        subject_label.setStyleSheet("font-size: 14px; color: #3498db;")
        layout.addWidget(subject_label)

        topic_label = QLabel(f"Тема: {self._event.description or '(не указана)'}")
        topic_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        layout.addWidget(topic_label)

        date_label = QLabel(f"Дата: {self._event.start_time.date()}")
        date_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        layout.addWidget(date_label)

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
        layout.addWidget(self._table)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_data(self):
        persons = self._person_service.get_all_persons()
        attendances = {a.person_id: a for a in self._attendance_service.get_event_attendance(self._event.event_id)}
        self._table.setRowCount(len(persons))

        for row, person in enumerate(persons):
            self._table.setItem(row, 0, QTableWidgetItem(person.label))
            self._table.item(row, 0).setData(Qt.UserRole, person.person_id)

            status = attendances.get(person.person_id)
            is_present = status is not None and status.status == AttendanceStatus.PRESENT
            status_text = "ПРИСУТСТВУЕТ" if is_present else "ОТСУТСТВУЕТ"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#27ae60") if is_present else QColor("#e74c3c"))
            self._table.setItem(row, 1, status_item)

    def _toggle_member(self, person_id: int):
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


# ---------- AddSubjectDialog ----------
class AddSubjectDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Добавить предмет в список")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("НОВЫЙ ПРЕДМЕТ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)

        form = QFormLayout()
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Название предмета")
        form.addRow("Название:", self._name_edit)

        self._topic_edit = QLineEdit()
        self._topic_edit.setPlaceholderText("Описание предмета (необязательно)")
        form.addRow("Описание:", self._topic_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Добавить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return self._name_edit.text().strip(), self._topic_edit.text().strip()


# ---------- AddToScheduleDialog ----------
class AddToScheduleDialog(QDialog):
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
        layout.setSpacing(15)

        title = QLabel("ДОБАВЛЕНИЕ ПРЕДМЕТА В РАСПИСАНИЕ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
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


# ---------- EditEventDialog ----------
class EditEventDialog(QDialog):
    def __init__(self, parent, event: BaseEvent, template_service):
        super().__init__(parent)
        self._event = event
        self._template_service = template_service
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("Редактировать событие")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("РЕДАКТИРОВАНИЕ СОБЫТИЯ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #f39c12;")
        layout.addWidget(title)

        form = QFormLayout()
        self._name_combo = QComboBox()
        templates = list(self._template_service.get_all_templates())
        templates.sort(key=lambda t: t.label.lower())
        self._template_map = {}
        for t in templates:
            self._name_combo.addItem(t.label, t.event_id)
            self._template_map[t.event_id] = t.label
        self._name_combo.setEditable(False)
        form.addRow("Предмет:", self._name_combo)

        self._topic_edit = QLineEdit()
        form.addRow("Тема:", self._topic_edit)

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
        self._topic_edit.setText(self._event.description)

    def get_data(self):
        return self._name_combo.currentText(), self._topic_edit.text().strip()


# ---------- ManualAttendanceDialog ----------
class ManualAttendanceDialog(QDialog):
    def __init__(self, parent, person_service, attendance_service, event):
        super().__init__(parent)
        self._person_service = person_service
        self._attendance_service = attendance_service
        self._event = event
        self.setWindowTitle(f"Ручная отметка - {event.label}")
        self.setModal(True)
        self.setMinimumWidth(300)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        persons = self._person_service.get_all_persons()
        self._combo = QComboBox()
        for p in persons:
            self._combo.addItem(p.label, p.person_id)
        layout.addWidget(QLabel("Выберите участника:"))
        layout.addWidget(self._combo)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Отметить присутствие")
        ok_btn.clicked.connect(self._mark)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _mark(self):
        person_id = self._combo.currentData()
        try:
            self._attendance_service.add_attendance(person_id, self._event.event_id, AttendanceStatus.PRESENT)
            QMessageBox.information(self, "Успех", "Участник отмечен.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))


# ---------- SubjectsManagementDialog (исправленный, с ViewModel) ----------
class SubjectsManagementDialog(QDialog):
    subjects_changed = Signal()

    def __init__(self, parent, view_model):
        super().__init__(parent)
        self._view_model = view_model
        self.setWindowTitle("Управление предметами")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_subjects()
        # Подключаем сигналы вьюмодели
        self._view_model.subjects_changed.connect(self._load_subjects)
        self._view_model.subjects_changed.connect(self.subjects_changed.emit)
        self._view_model.show_warning.connect(lambda msg: QMessageBox.warning(self, "Ошибка", msg))
        self._view_model.show_success.connect(lambda msg: QMessageBox.information(self, "Успех", msg))

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("СПИСОК ПРЕДМЕТОВ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Название", "Описание"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_subject)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(self._edit_subject)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete_subject)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_subjects(self):
        templates = self._view_model.get_all_templates()
        self._table.setRowCount(len(templates))
        for row, t in enumerate(templates):
            self._table.setItem(row, 0, QTableWidgetItem(t.label))
            self._table.setItem(row, 1, QTableWidgetItem(t.description or ""))
            self._table.item(row, 0).setData(Qt.UserRole, t.event_id)

    def _add_subject(self):
        name, ok = QInputDialog.getText(self, "Новый предмет", "Название предмета:")
        if ok and name:
            desc, ok2 = QInputDialog.getText(self, "Описание", "Описание (необязательно):")
            if ok2:
                self._view_model.add_template(name, desc)

    def _edit_subject(self):
        current_row = self._table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для редактирования.")
            return
        subject_id = self._table.item(current_row, 0).data(Qt.UserRole)
        old_name = self._table.item(current_row, 0).text()
        old_desc = self._table.item(current_row, 1).text()
        new_name, ok = QInputDialog.getText(self, "Редактирование", "Название:", text=old_name)
        if ok and new_name:
            new_desc, ok2 = QInputDialog.getText(self, "Редактирование", "Описание:", text=old_desc)
            if ok2:
                self._view_model.update_template(subject_id, new_name, new_desc)

    def _delete_subject(self):
        current_row = self._table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления.")
            return
        subject_id = self._table.item(current_row, 0).data(Qt.UserRole)
        subject_name = self._table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить предмет '{subject_name}'?\nВсе связанные занятия также будут удалены из расписания.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._view_model.delete_template(subject_id, subject_name)

# ---------- AttendanceDetailsDialog ----------
class AttendanceDetailsDialog(QDialog):
    def __init__(self, parent, attendance_service, person_service, event: BaseEvent):
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
        layout.setSpacing(15)

        title = QLabel("СПИСОК ОТМЕТИВШИХСЯ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(1)
        self._table.setHorizontalHeaderLabels(["Участник"])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.verticalHeader().setVisible(False)
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