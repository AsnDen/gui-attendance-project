from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QInputDialog, QMessageBox, QDialog
)
from .base import BaseDialog
from .qr_dialogs import QRScanDialog
from roll.view_models.qr_scanner_viewmodel import QRScannerViewModel


class GroupManagementDialog(BaseDialog):
    def __init__(self, parent, person_service, identifier_service):
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
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["ФИО", "QR-код", ""])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.itemDoubleClicked.connect(self._on_item_double_clicked)
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
        self._person_ids = []
        for row, person in enumerate(persons):
            self._person_ids.append(person.person_id)
            name_item = QTableWidgetItem(person.label)
            self._table.setItem(row, 0, name_item)
            identifiers = self._identifier_service.get_person_identifiers(person.person_id)
            has_qr = len(identifiers) > 0
            qr_status = "Привязан" if has_qr else "Не привязан"
            qr_item = QTableWidgetItem(qr_status)
            if not has_qr:
                qr_item.setForeground(QColor("#7f8c8d"))
            self._table.setItem(row, 1, qr_item)
            btn = QPushButton("Удалить QR" if has_qr else "Привязать QR")
            if has_qr:
                btn.clicked.connect(lambda checked, pid=person.person_id: self._unbind_qr(pid))
            else:
                btn.clicked.connect(lambda checked, pid=person.person_id: self._bind_qr(pid))
            self._table.setCellWidget(row, 2, btn)

    def _on_item_double_clicked(self, item):
        if item.column() != 0:
            return
        row = item.row()
        person_id = self._person_ids[row]
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Редактирование", "Введите новое ФИО:", text=old_name)
        if ok and new_name and new_name != old_name:
            try:
                self._person_service.update_person(person_id, label=new_name)
                self._load_members()
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
            person_id = self._person_ids[current_row]
            person = self._person_service.get_person(person_id)
            if person and QMessageBox.question(self, "Подтверждение", f"Удалить '{person.label}'?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
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
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                identifiers = self._identifier_service.get_person_identifiers(person_id)
                for ident in identifiers:
                    self._identifier_service.delete_identifier(ident.identifier_id)
                QMessageBox.information(self, "Успех", f"QR-код удалён у {person.label}")
                self._load_members()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))