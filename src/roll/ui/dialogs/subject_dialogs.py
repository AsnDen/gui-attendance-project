from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog
)
from .base import BaseDialog

class SubjectNameDescriptionDialog(BaseDialog):
    def __init__(self, parent, title="Ввод данных", label="", description=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.name_edit = QLineEdit(label)
        self.name_edit.setPlaceholderText("Название")
        self.desc_edit = QLineEdit(description)
        self.desc_edit.setPlaceholderText("Описание (необязательно)")
        form.addRow("Название:", self.name_edit)
        form.addRow("Описание:", self.desc_edit)
        layout.addLayout(form)
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_data(self):
        return self.name_edit.text().strip(), self.desc_edit.text().strip()


class SubjectsManagementDialog(BaseDialog):
    subjects_changed = Signal()

    def __init__(self, parent, view_model):
        super().__init__(parent)
        self._view_model = view_model
        self.setWindowTitle("Управление предметами")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_subjects()
        self._view_model.subjects_changed.connect(self._load_subjects)
        self._view_model.subjects_changed.connect(self.subjects_changed.emit)
        self._view_model.show_warning.connect(lambda msg: QMessageBox.warning(self, "Ошибка", msg))

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel("СПИСОК ПРЕДМЕТОВ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        layout.addWidget(title)
        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Название", "Описание"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.itemDoubleClicked.connect(self._edit_subject_by_double_click)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_subject)
        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete_subject)
        btn_layout.addWidget(add_btn)
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
        from .subject_dialogs import SubjectNameDescriptionDialog
        dialog = SubjectNameDescriptionDialog(self, "Новый предмет")
        if dialog.exec() == QDialog.Accepted:
            name, desc = dialog.get_data()
            if name:
                self._view_model.add_template(name, desc)

    def _edit_subject_by_double_click(self, item):
        row = item.row()
        subject_id = self._table.item(row, 0).data(Qt.UserRole)
        old_name = self._table.item(row, 0).text()
        old_desc = self._table.item(row, 1).text()
        from .subject_dialogs import SubjectNameDescriptionDialog
        dialog = SubjectNameDescriptionDialog(self, "Редактирование предмета", old_name, old_desc)
        if dialog.exec() == QDialog.Accepted:
            new_name, new_desc = dialog.get_data()
            if new_name:
                self._view_model.update_template(subject_id, new_name, new_desc)

    def _delete_subject(self):
        current_row = self._table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления.")
            return
        subject_id = self._table.item(current_row, 0).data(Qt.UserRole)
        subject_name = self._table.item(current_row, 0).text()
        reply = QMessageBox.question(self, "Подтверждение",
                                     f"Удалить предмет '{subject_name}'?\nВсе связанные занятия также будут удалены.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._view_model.delete_template(subject_id, subject_name)