# WARNING (asnden): DONT WORK FOR NOW

from database import Database
from models import Member, ScheduleItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class BindQRDialog(QDialog):
    def __init__(self, parent, db: Database, member: Member) -> None:
        super().__init__(parent)
        self._db = db
        self._member = member
        self.setWindowTitle(f"Привязка QR-кода - {member.name}")
        self.setModal(True)
        self.setMinimumWidth(450)
        self._setup_ui()
        self._scanned_qr = None

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("📱 ПРИВЯЗКА QR-КОДА")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9b59b6;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info = QLabel(f"Участник: {self._member.name}")
        info.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        layout.addWidget(info)

        layout.addWidget(QLabel("Отсканируйте QR-код участника:"))

        self._qr_display = QLabel("📷 [Здесь будет отображаться отсканированный QR]")
        self._qr_display.setStyleSheet(
            "background-color: #34495e; border-radius: 8px; padding: 20px; color: #7f8c8d;"
        )
        self._qr_display.setAlignment(Qt.AlignCenter)
        self._qr_display.setMinimumHeight(100)
        layout.addWidget(self._qr_display)

        btn_layout = QHBoxLayout()
        self._scan_btn = QPushButton("🎥 Сканировать с камеры")
        self._scan_btn.clicked.connect(self._simulate_scan)
        self._manual_btn = QPushButton("⌨️ Ввести вручную")
        self._manual_btn.clicked.connect(self._manual_input)
        btn_layout.addWidget(self._scan_btn)
        btn_layout.addWidget(self._manual_btn)
        layout.addLayout(btn_layout)

        btn_layout2 = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout2.addWidget(save_btn)
        btn_layout2.addWidget(cancel_btn)
        layout.addLayout(btn_layout2)

    def _simulate_scan(self) -> None:
        self._scanned_qr = f"MEMBER_{self._member.id}_SCAN"
        self._qr_display.setText(f"📱 Отсканировано: {self._scanned_qr}")
        self._qr_display.setStyleSheet(
            "background-color: #27ae60; border-radius: 8px; padding: 20px; color: white;"
        )

    def _manual_input(self) -> None:
        qr, ok = QInputDialog.getText(self, "Ввод QR-кода", "Введите QR-код участника:")
        if ok and qr:
            self._scanned_qr = qr
            self._qr_display.setText(f"📱 Введено: {self._scanned_qr}")
            self._qr_display.setStyleSheet(
                "background-color: #27ae60; border-radius: 8px; padding: 20px; color: white;"
            )

    def get_qr_code(self) -> str | None:
        return self._scanned_qr


class AddScheduleDialog(QDialog):
    def __init__(self, parent, date: str) -> None:
        super().__init__(parent)
        self._date = date
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle(f"Добавить предмет на {self._date}")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("📅 ДОБАВЛЕНИЕ ПРЕДМЕТА")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)

        date_label = QLabel(f"Дата: {self._date}")
        date_label.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(date_label)

        form = QFormLayout()
        form.setSpacing(12)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Например: Математика")
        form.addRow("📝 Предмет:", self._name_edit)

        self._topic_edit = QLineEdit()
        self._topic_edit.setPlaceholderText("Тема занятия")
        form.addRow("📖 Тема:", self._topic_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("✅ Добавить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def get_data(self) -> tuple[str, str]:
        return self._name_edit.text().strip(), self._topic_edit.text().strip()


class AttendanceDialog(QDialog):
    def __init__(self, parent, db: Database, schedule_item: ScheduleItem) -> None:
        super().__init__(parent)
        self._db = db
        self._schedule_item = schedule_item
        self.setWindowTitle(
            f"Посещаемость: {schedule_item.subject_name} - {schedule_item.date}"
        )
        self.setModal(True)
        self.setMinimumSize(500, 500)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("📋 ПОСЕЩАЕМОСТЬ")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1abc9c;")
        layout.addWidget(title)

        subject_label = QLabel(f"Предмет: {self._schedule_item.subject_name}")
        subject_label.setStyleSheet("font-size: 14px; color: #3498db;")
        layout.addWidget(subject_label)

        topic_label = QLabel(f"Тема: {self._schedule_item.topic or '(не указана)'}")
        topic_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        layout.addWidget(topic_label)

        date_label = QLabel(f"Дата: {self._schedule_item.date}")
        date_label.setStyleSheet("font-size: 12px; color: #ecf0f1;")
        layout.addWidget(date_label)

        btn_layout = QHBoxLayout()
        self._all_btn = QPushButton("✅ Отметить всех")
        self._all_btn.clicked.connect(self._mark_all)
        self._clear_btn = QPushButton("❌ Снять всех")
        self._clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(self._all_btn)
        btn_layout.addWidget(self._clear_btn)
        layout.addLayout(btn_layout)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Участник", "Статус", ""])
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 250)
        layout.addWidget(self._table)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_data(self) -> None:
        members = self._db.get_members()
        present_ids = self._schedule_item.member_ids

        self._table.setRowCount(len(members))

        for row, member in enumerate(members):
            self._table.setItem(row, 0, QTableWidgetItem(member.display_name()))
            self._table.item(row, 0).setData(Qt.UserRole, member.id)

            is_present = member.id in present_ids
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)

            status_label = QLabel("✅ ПРИСУТСТВУЕТ" if is_present else "❌ ОТСУТСТВУЕТ")
            status_label.setStyleSheet(
                "color: #27ae60;" if is_present else "color: #e74c3c;"
            )
            status_layout.addWidget(status_label)
            status_layout.addStretch()
            self._table.setCellWidget(row, 1, status_widget)

            btn = QPushButton("❌ Снять" if is_present else "✅ Отметить")
            btn.clicked.connect(
                lambda checked, m_id=member.id: self._toggle_member(m_id)
            )
            self._table.setCellWidget(row, 2, btn)

    def _toggle_member(self, member_id: int) -> None:
        if member_id in self._schedule_item.member_ids:
            self._db.unmark_attendance(self._schedule_item.id, member_id)
            self._schedule_item.member_ids.remove(member_id)
        elif self._db.mark_attendance(self._schedule_item.id, member_id):
            self._schedule_item.member_ids.append(member_id)
        self._load_data()

    def _mark_all(self) -> None:
        members = self._db.get_members()
        for member in members:
            if member.id not in self._schedule_item.member_ids:
                self._db.mark_attendance(self._schedule_item.id, member.id)
                self._schedule_item.member_ids.append(member.id)
        self._load_data()

    def _clear_all(self) -> None:
        members = self._db.get_members()
        for member in members:
            if member.id in self._schedule_item.member_ids:
                self._db.unmark_attendance(self._schedule_item.id, member.id)
                self._schedule_item.member_ids.remove(member.id)
        self._load_data()


class EditScheduleDialog(QDialog):
    def __init__(self, parent, schedule_item: ScheduleItem) -> None:
        super().__init__(parent)
        self._schedule_item = schedule_item
        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Редактировать предмет")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("✏️ РЕДАКТИРОВАНИЕ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #f39c12;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self._name_edit = QLineEdit()
        form.addRow("📝 Предмет:", self._name_edit)

        self._topic_edit = QLineEdit()
        form.addRow("📖 Тема:", self._topic_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _load_data(self) -> None:
        self._name_edit.setText(self._schedule_item.subject_name)
        self._topic_edit.setText(self._schedule_item.topic)

    def get_data(self) -> tuple[str, str]:
        return self._name_edit.text().strip(), self._topic_edit.text().strip()


class GroupManagementDialog(QDialog):
    def __init__(self, parent, db: Database) -> None:
        super().__init__(parent)
        self._db = db
        self.setWindowTitle("👥 Управление группой")
        self.setModal(True)
        self.setMinimumSize(500, 550)
        self._setup_ui()
        self._load_members()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("👥 СПИСОК ГРУППЫ")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["ID", "ФИО", "QR-код"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._table.verticalHeader().setDefaultSectionSize(35)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3e50;
                alternate-background-color: #34495e;
                gridline-color: #1abc9c;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            }
        """)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Добавить")
        add_btn.clicked.connect(self._add_member)
        delete_btn = QPushButton("🗑️ Удалить")
        delete_btn.clicked.connect(self._delete_member)
        bind_btn = QPushButton("📱 Привязать QR")
        bind_btn.clicked.connect(self._bind_qr)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(bind_btn)
        layout.addLayout(btn_layout)

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _load_members(self) -> None:
        members = self._db.get_members()
        self._table.setRowCount(len(members))

        for row, member in enumerate(members):
            self._table.setItem(row, 0, QTableWidgetItem(str(member.id)))
            self._table.setItem(row, 1, QTableWidgetItem(member.name))
            qr_display = member.qr_code or "(не привязан)"
            qr_item = QTableWidgetItem(qr_display)
            if not member.qr_code:
                qr_item.setForeground(QColor("#7f8c8d"))
            self._table.setItem(row, 2, qr_item)
            self._table.item(row, 0).setData(Qt.UserRole, member.id)

        self._table.resizeRowsToContents()

    def _add_member(self) -> None:
        name, ok = QInputDialog.getText(self, "Новый участник", "Введите ФИО:")
        if ok and name:
            self._db.add_member(name)
            self._load_members()

    def _delete_member(self) -> None:
        current_row = self._table.currentRow()
        if current_row >= 0:
            member_id = self._table.item(current_row, 0).data(Qt.UserRole)
            member = self._db.get_member_by_id(member_id)
            if (
                member
                and QMessageBox.question(
                    self, "Подтверждение", f"Удалить '{member.name}'?"
                )
                == QMessageBox.Yes
            ):
                self._db.delete_member(member_id)
                self._load_members()

    def _bind_qr(self) -> None:
        current_row = self._table.currentRow()
        if current_row >= 0:
            member_id = self._table.item(current_row, 0).data(Qt.UserRole)
            member = self._db.get_member_by_id(member_id)
            if member:
                dialog = BindQRDialog(self, self._db, member)
                if dialog.exec():
                    qr_code = dialog.get_qr_code()
                    if qr_code:
                        self._db.update_member_qr(member_id, qr_code)
                        self._load_members()
                        QMessageBox.information(
                            self, "Успех", f"QR-код привязан к {member.name}"
                        )
