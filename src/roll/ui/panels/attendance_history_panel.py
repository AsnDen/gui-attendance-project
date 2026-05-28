from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)

from roll.core import AttendanceStatus
from roll.services import AttendanceService, PersonService, EventService


class AttendanceHistoryPanel(QFrame):
    def __init__(self, attendance_service: AttendanceService,
                 person_service: PersonService,
                 event_service: EventService):
        super().__init__()
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._event_service = event_service
        self._current_event = None
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 12px;
                margin: 5px;
            }
            QLabel#title {
                color: #ecf0f1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2c3e50;
                border-radius: 8px;
            }
            QTableWidget {
                background-color: #2c3e50;
                alternate-background-color: #34495e;
                color: #ecf0f1;
                gridline-color: #1abc9c;
            }
            QHeaderView::section {
                background-color: #1abc9c;
                color: #2c3e50;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton {
                background-color: #1abc9c;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #16a085;
                color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._title_label = QLabel("ИСТОРИЯ ПОСЕЩАЕМОСТИ")
        self._title_label.setObjectName("title")
        self._title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_label)

        self._export_csv_btn = QPushButton("Экспорт в CSV")
        self._export_csv_btn.clicked.connect(self._export_csv)
        layout.addWidget(self._export_csv_btn)

        self._table = QTableWidget()
        self._table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

        self._info_label = QLabel("Выберите предмет в расписании")
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setStyleSheet("color: #1abc9c;")
        layout.addWidget(self._info_label)

    def set_event(self, event):
        self._current_event = event
        if event:
            self._title_label.setText(f"ИСТОРИЯ ПОСЕЩАЕМОСТИ: {event.label}")
            self.load_history()
        else:
            self._title_label.setText("ИСТОРИЯ ПОСЕЩАЕМОСТИ")
            self._table.clear()
            self._table.setRowCount(0)
            self._info_label.setText("Выберите предмет в расписании")

    def load_history(self):
        if not self._current_event:
            return

        subject_label = self._current_event.label
        all_events = self._event_service.get_all_events()
        subject_events = [e for e in all_events if e.label == subject_label]
        subject_events.sort(key=lambda e: e.start_time)

        persons = list(self._person_service.get_all_persons())
        persons.sort(key=lambda p: p.label.lower())

        attendance_percent = []
        for person in persons:
            present_count = 0
            for ev in subject_events:
                att_list = self._attendance_service.get_event_attendance(ev.event_id)
                if any(a.person_id == person.person_id and a.status == AttendanceStatus.PRESENT for a in att_list):
                    present_count += 1
            percent = (present_count / len(subject_events) * 100) if subject_events else 0
            attendance_percent.append(percent)

        self._table.setColumnCount(len(subject_events) + 2)
        self._table.setHorizontalHeaderItem(0, QTableWidgetItem("ФИО"))
        self._table.setHorizontalHeaderItem(1, QTableWidgetItem("% посещения"))
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self._table.setColumnWidth(0, 350)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self._table.setColumnWidth(1, 100)

        self._table.horizontalHeader().setMinimumSectionSize(100)

        for col, ev in enumerate(subject_events, start=2):
            date_str = ev.start_time.strftime("%d.%m.%Y")
            self._table.setHorizontalHeaderItem(col, QTableWidgetItem(date_str))
            self._table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

        self._table.setRowCount(len(persons))
        for row, person in enumerate(persons):
            name_item = QTableWidgetItem(person.label)
            self._table.setItem(row, 0, name_item)
            percent_item = QTableWidgetItem(f"{attendance_percent[row]:.1f}%")
            percent_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 1, percent_item)
            for col, ev in enumerate(subject_events, start=2):
                att_list = self._attendance_service.get_event_attendance(ev.event_id)
                present = any(a.person_id == person.person_id and a.status == AttendanceStatus.PRESENT for a in att_list)
                mark = "✔" if present else "✘"
                item = QTableWidgetItem(mark)
                item.setTextAlignment(Qt.AlignCenter)
                item.setForeground(QColor("#27ae60") if present else QColor("#e74c3c"))
                self._table.setItem(row, col, item)

        self._info_label.setText(f"Всего занятий: {len(subject_events)}")

    def _export_csv(self):
        if not self._current_event:
            QMessageBox.warning(self, "Экспорт", "Сначала выберите предмет.")
            return
        if self._table.rowCount() == 0 or self._table.columnCount() == 0:
            QMessageBox.warning(self, "Экспорт", "Нет данных для экспорта.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "", "CSV files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                headers = []
                for col in range(self._table.columnCount()):
                    headers.append(self._table.horizontalHeaderItem(col).text())
                f.write(",".join(headers) + "\n")
                for row in range(self._table.rowCount()):
                    row_data = []
                    for col in range(self._table.columnCount()):
                        item = self._table.item(row, col)
                        row_data.append(item.text() if item else "")
                    f.write(",".join(row_data) + "\n")
            QMessageBox.information(self, "Экспорт", "CSV сохранён.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def refresh(self):
        if self._current_event:
            self.load_history()