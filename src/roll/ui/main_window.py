from typing import override

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QWidget

from roll.ui.panels import CalendarPanel, DayEventPanel, ScannerPanel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        self.setWindowTitle("📱 Система учёта посещаемости с QR")
        self.setGeometry(100, 100, 1400, 800)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self._day_panel: DayEventPanel = DayEventPanel()
        main_layout.addWidget(self._day_panel)

        self._scanner_panel: ScannerPanel = ScannerPanel()
        main_layout.addWidget(self._scanner_panel, 1)

        self._calendar_panel: CalendarPanel = CalendarPanel()
        main_layout.addWidget(self._calendar_panel)

        menubar = self.menuBar()
        group_menu = menubar.addMenu("👥 Группа")
        manage_action = group_menu.addAction("Управление группой (привязка QR)")
        _ = manage_action.triggered.connect(self._manage_group)

        help_menu = menubar.addMenu("❓ Помощь")
        about_action = help_menu.addAction("О программе")
        _ = about_action.triggered.connect(self._show_about)

        self.statusBar().showMessage("Готов")
        self.statusBar().setStyleSheet(
            "QStatusBar { background-color: #2c3e50; color: #1abc9c; }"
        )

    def _setup_connections(self) -> None:
        # _ = self._calendar_panel.date_selected.connect(self._on_date_selected)
        _ = self._scanner_panel.qr_scanned.connect(self._on_qr_scanned)
        # _ = self._day_panel.subject_selected.connect(self._on_subject_selected)

    def _on_date_selected(self, date_str: str) -> None:
        # self._day_panel.set_date(date_str)
        # self.statusBar().showMessage(f"Выбрана дата: {date_str}")
        pass

    def _on_subject_selected(self, schedule_item) -> None:
        # self._scanner_panel.update_status(
        #     f"✅ Предмет: {schedule_item.subject_name} | Сканируйте QR-код"
        # )
        # self.statusBar().showMessage(f"Выбран предмет: {schedule_item.subject_name}")
        pass

    def _on_qr_scanned(self, qr_data: str) -> None:
        # current_item = self._day_panel.get_current_item()
        #
        # if not current_item:
        #     self._scanner_panel.update_status(
        #         "❌ Сначала выберите предмет в левой панели!", True
        #     )
        #     return
        #
        # member = self._db.get_member_by_qr(qr_data)
        #
        # if not member:
        #     self._scanner_panel.update_status(
        #         f"❌ Участник с QR '{qr_data[:20]}...' не найден! Привяжите QR в меню Группа",
        #         True,
        #     )
        #     return
        #
        # success = self._db.mark_attendance(current_item.id, member.id)
        #
        # if success:
        #     self._scanner_panel.update_status(f"✅ ОТМЕЧЕН: {member.name}")
        #     self.statusBar().showMessage(f"Отмечен {member.name}")
        #     QMessageBox.information(self, "Успех", f"✅ {member.name} отмечен(а)")
        #     self._day_panel.refresh()
        # else:
        #     self._scanner_panel.update_status(
        #         f"⚠️ {member.name} уже отмечен(а) на этом занятии!", True
        #     )
        pass

    def _manage_group(self) -> None:
        # dialog = GroupManagementDialog(self, self._db)
        # _ = dialog.exec()
        pass

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            """📱 Система учёта посещаемости с QR-кодами
            Версия: 1.0
            Функции:
            • Календарь с расписанием по дням
            • Добавление предметов на конкретные даты
            • Указание темы занятия
            • Отметка посещаемости по QR-кодам (сканер)
            • Привязка QR-кодов к участникам
            • Просмотр посещаемости (двойной клик)
            • Логирование всех действий
            © Семестровый проект.""",
        )

    @override
    def closeEvent(self, event: QEvent) -> None:
        reply = QMessageBox.question(
            self,
            "Выход",
            "Закрыть приложение?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
