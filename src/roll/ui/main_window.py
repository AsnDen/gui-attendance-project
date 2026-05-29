from typing import override

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QMessageBox, QWidget

from roll.core import AttendanceStatus, BaseEvent
from roll.core.interfaces import IAttendanceService, IIdentifierService, IPersonService
from roll.ui.dialogs import (
    GroupManagementDialog, SubjectsManagementDialog, ManualAttendanceDialog,
    QRMarkDialog, QRScanDialog
)
from roll.ui.panels import EventDetailsPanel, AttendanceHistoryPanel, CalendarPanel
from roll.view_models import QRScannerViewModel, ViewModelFactory
from roll.view_models.subjects_management_viewmodel import SubjectsManagementViewModel


class MainWindow(QMainWindow):
    def __init__(
        self,
        view_model_factory: ViewModelFactory,
        attendance_service: IAttendanceService,
        person_service: IPersonService,
        identifier_service: IIdentifierService,
        event_service,
        template_service,
    ) -> None:
        super().__init__()

        self._view_model_factory = view_model_factory
        self._attendance_service = attendance_service
        self._person_service = person_service
        self._identifier_service = identifier_service
        self._event_service = event_service
        self._template_service = template_service

        self._current_selected_event: BaseEvent | None = None

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Система учёта посещаемости с QR")
        self.setGeometry(100, 100, 1400, 800)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self._details_panel = EventDetailsPanel(
            attendance_service=self._attendance_service,
            person_service=self._person_service
        )
        main_layout.addWidget(self._details_panel)

        self._history_panel = AttendanceHistoryPanel(
            attendance_service=self._attendance_service,
            person_service=self._person_service,
            event_service=self._event_service
        )
        main_layout.addWidget(self._history_panel, 1)

        calendar_view_model = self._view_model_factory.create_calendar_view_model()
        self._calendar_panel = CalendarPanel(
            calendar_view_model,
            self._event_service,
            self._template_service
        )
        main_layout.addWidget(self._calendar_panel)

        menubar = self.menuBar()
        group_menu = menubar.addMenu("Группа")
        manage_action = group_menu.addAction("Управление группой (привязка QR)")
        manage_action.triggered.connect(self._manage_group)

        subjects_menu = menubar.addMenu("Предметы")
        list_subjects_action = subjects_menu.addAction("Список предметов")
        list_subjects_action.triggered.connect(self._manage_subjects)

        help_menu = menubar.addMenu("Помощь")
        about_action = help_menu.addAction("О программе")
        about_action.triggered.connect(self._show_about)

        self.statusBar().showMessage("Готов")
        self.statusBar().setStyleSheet("QStatusBar { background-color: #2c3e50; color: #1abc9c; }")

    def _setup_connections(self) -> None:
        self._calendar_panel.event_selected.connect(self._on_event_selected)
        self._calendar_panel.data_changed.connect(self._on_data_changed)
        self._details_panel.mark_attendance_requested.connect(self._on_qr_mark)
        self._details_panel.manual_mark_requested.connect(self._on_manual_mark)

    def _on_event_selected(self, event: BaseEvent | None):
        self._current_selected_event = event
        self._details_panel.set_event(event)
        self._history_panel.set_event(event)
        if event:
            self.statusBar().showMessage(f"Выбран предмет: {event.label}")
        else:
            self.statusBar().showMessage("Выбор сброшен")

    def _on_data_changed(self):
        if self._current_selected_event:
            try:
                self._event_service.get_event(self._current_selected_event.event_id)
                self._history_panel.refresh()
                self._details_panel.refresh()
            except:
                self._on_event_selected(None)

    def _on_qr_mark(self, event: BaseEvent) -> None:
        scanner_vm = QRScannerViewModel()

        def mark_attendance(qr_hash: str):
            self._process_qr_mark(qr_hash, event)

        dialog = QRMarkDialog(self, scanner_vm, mark_attendance)
        dialog.exec()

    def _process_qr_mark(self, qr_hash: str, event: BaseEvent):
        person = self._identifier_service.find_person_by_hash(qr_hash)
        if not person:
            QMessageBox.warning(self, "Ошибка", "QR-код не найден. Привяжите его в меню Группа.")
            return
        try:
            self._attendance_service.add_attendance(person.person_id, event.event_id, AttendanceStatus.PRESENT)
            self.statusBar().showMessage(f"Отмечен: {person.label}")
            self._details_panel.refresh()
            self._history_panel.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def _on_manual_mark(self, event: BaseEvent):
        dialog = ManualAttendanceDialog(self, self._person_service, self._attendance_service, event)
        if dialog.exec():
            self._details_panel.refresh()
            self._history_panel.refresh()

    def _manage_group(self) -> None:
        dialog = GroupManagementDialog(self, self._person_service, self._identifier_service)
        dialog.exec()
        if self._current_selected_event:
            try:
                self._event_service.get_event(self._current_selected_event.event_id)
                self._details_panel.refresh()
                self._history_panel.refresh()
            except:
                self._on_event_selected(None)

    def _manage_subjects(self) -> None:
        vm = SubjectsManagementViewModel(self._template_service, self._event_service)
        dialog = SubjectsManagementDialog(self, vm)
        dialog.subjects_changed.connect(self._on_subjects_changed)
        dialog.exec()

    def _on_subjects_changed(self):
        current_date = self._calendar_panel._calendar.selectedDate()
        self._calendar_panel._view_model.select_date(current_date)
        self._calendar_panel._view_model.load_events()
        if self._current_selected_event:
            try:
                self._event_service.get_event(self._current_selected_event.event_id)
            except:
                self._on_event_selected(None)
        self._details_panel.refresh()
        self._history_panel.refresh()

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Система учёта посещаемости с QR-кодами\n\n"
            "Версия: 3.0\n\n"
            "Функции:\n"
            "- Календарь и расписание на день\n"
            "- История посещаемости по каждому предмету\n"
            "- Отметка по QR (отдельное окно с камерой)\n"
            "- Ручная отметка\n"
            "- Управление предметами и группой\n"
            "- Привязка/удаление QR, редактирование ФИО\n\n"
            "Семестровый проект",
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
