from datetime import date
from typing import override

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QWidget

from roll.core import AttendanceStatus, BaseEvent
from roll.core.interfaces import IAttendanceService, IIdentifierService, IPersonService
from roll.ui.panels import CalendarPanel, DayEventsPanel, ScannerPanel
from roll.view_models import ViewModelFactory


class MainWindow(QMainWindow):
    def __init__(
        self,
        view_model_factory: ViewModelFactory,
        attendance_service: IAttendanceService,
        person_service: IPersonService,
        identifier_service: IIdentifierService,
    ) -> None:
        super().__init__()

        self._view_model_factory = view_model_factory
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._identifier_service = identifier_service

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

        self._day_panel: DayEventsPanel = DayEventsPanel()
        main_layout.addWidget(self._day_panel)

        self._scanner_panel: ScannerPanel = ScannerPanel()
        main_layout.addWidget(self._scanner_panel, 1)

        calendar_view_model = self._view_model_factory.create_calendar_view_moder()
        self._calendar_panel: CalendarPanel = CalendarPanel(calendar_view_model)
        main_layout.addWidget(self._calendar_panel)

        menubar = self.menuBar()
        group_menu = menubar.addMenu("👥 Группа")
        manage_action = group_menu.addAction("Управление группой (привязка QR)")
        manage_action.triggered.connect(self._manage_group)

        help_menu = menubar.addMenu("❓ Помощь")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self._show_about)

        self.statusBar().showMessage("Готов")
        self.statusBar().setStyleSheet(
            "QStatusBar { background-color: #2c3e50; color: #1abc9c; }"
        )

    def _setup_connections(self) -> None:
        self._calendar_panel.date_selected.connect(self._on_date_selected)
        self._scanner_panel.qr_scanned.connect(self._on_qr_scanned)
        self._day_panel.event_selected.connect(self._on_event_selected)

    def _on_date_selected(self, date_str: str) -> None:
        self._day_panel.set_date(date_str)
        # Загружаем события на выбранную дату
        events = self._view_model_factory.event_service.get_day_events(date.fromisoformat(date_str))
        self._day_panel.set_events(list(events))
        self.statusBar().showMessage(f"Выбрана дата: {date_str}")

    def _on_event_selected(self, event: BaseEvent) -> None:
        self._scanner_panel.update_status(
            f"✅ Предмет: {event.label} | Сканируйте QR-код"
        )
        self.statusBar().showMessage(f"Выбран предмет: {event.label}")

    def _on_qr_scanned(self, qr_data: str) -> None:
        current_event = self._day_panel.get_current_event()
        if not current_event:
            self._scanner_panel.update_status(
                "❌ Сначала выберите предмет в левой панели!", True
            )
            return

        person = self._identifier_service.find_person_by_hash(qr_data)
        if not person:
            self._scanner_panel.update_status(
                f"❌ Участник с QR '{qr_data[:20]}...' не найден! Привяжите QR в меню Группа",
                True,
            )
            return

        try:
            attendance_id = self._attendance_service.add_attendance(
                person.person_id, current_event.event_id, AttendanceStatus.PRESENT
            )
            self._scanner_panel.update_status(f"✅ ОТМЕЧЕН: {person.label}")
            self.statusBar().showMessage(f"Отмечен {person.label}")
            QMessageBox.information(self, "Успех", f"✅ {person.label} отмечен(а)")
            # Здесь можно обновить отображение посещаемости, если нужно
            # self._day_panel.refresh()
        except Exception as e:
            self._scanner_panel.update_status(f"⚠️ {person.label} уже отмечен(а) или ошибка: {e}", True)

    def _manage_group(self) -> None:
        # TODO: реализовать диалог управления группой
        QMessageBox.information(self, "Информация", "Управление группой будет реализовано позже.")

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