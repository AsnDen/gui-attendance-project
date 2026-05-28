from datetime import date
from PySide6.QtCore import QObject, Signal

from roll.core import AttendanceStatus
from roll.services import EventService, AttendanceService, PersonService


class DayEventsViewModel(QObject):
    data_changed = Signal()
    show_warning = Signal(str)
    # show_success удалён

    def __init__(self, event_service: EventService,
                 attendance_service: AttendanceService,
                 person_service: PersonService) -> None:
        super().__init__()
        self._event_service = event_service
        self._attendance_service = attendance_service
        self._person_service = person_service

    def get_day_events(self, date_str: str):
        dt = date.fromisoformat(date_str)
        return self._event_service.get_day_events(dt)

    def update_event(self, event_id: int, label: str, description: str) -> None:
        if not label.strip():
            self.show_warning.emit("Название события не может быть пустым!")
            return
        try:
            self._event_service.update_event(event_id, label=label, description=description)
            self.data_changed.emit()
        except Exception as e:
            self.show_warning.emit(str(e))

    def delete_event(self, event_id: int, label: str) -> None:
        try:
            self._event_service.delete_event(event_id)
            self.data_changed.emit()
        except Exception as e:
            self.show_warning.emit(str(e))

    def delete_all_events_by_label(self, label: str) -> None:
        try:
            deleted = 0
            for ev in self._event_service.get_all_events():
                if ev.label == label:
                    self._event_service.delete_event(ev.event_id)
                    deleted += 1
            self.data_changed.emit()
        except Exception as e:
            self.show_warning.emit(str(e))

    def get_attendance_count(self, event_id: int) -> int:
        attendances = self._attendance_service.get_event_attendance(event_id)
        return sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)

    def open_attendance_dialog(self, event, parent_widget):
        from roll.ui.dialogs import AttendanceDialog
        dialog = AttendanceDialog(parent_widget,
                                  self._attendance_service,
                                  self._person_service,
                                  event)
        dialog.data_changed.connect(self.data_changed.emit)
        return dialog.exec()
