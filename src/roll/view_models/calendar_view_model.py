from datetime import UTC, date, datetime, time, timedelta

from PySide6.QtCore import QDate, QObject, Signal

from roll.core import (
    BaseEvent,
    BaseEventTemplate,
    EventTemplate,
    IEventService,
    IEventTemplateService,
)


class CalendarPanelViewModel(QObject):
    event_changed = Signal(list)
    template_changed = Signal(list)
    show_warning = Signal(str)
    # show_success удалён
    date_changed = Signal(str)

    def __init__(
        self, event_service: IEventService, template_service: IEventTemplateService
    ) -> None:
        super().__init__()
        self._event_service = event_service
        self._template_service = template_service

        self._events: list[BaseEvent] = []
        self._templates: list[BaseEventTemplate] = []
        self._selected_date: str = datetime.now(tz=UTC).date().isoformat()

    @property
    def events(self) -> list[BaseEvent]:
        return self._events

    @property
    def templates(self) -> list[BaseEventTemplate]:
        return self._templates

    @property
    def selected_date(self) -> str:
        return self._selected_date

    def select_date(self, date: QDate) -> None:
        new_date_str = date.toString("yyyy-MM-dd")
        if self._selected_date != new_date_str:
            self._selected_date = new_date_str
            self.date_changed.emit(self._selected_date)

    def load_events(self) -> None:
        current_date = date.fromisoformat(self._selected_date)
        self._events = list(self._event_service.get_day_events(current_date))
        self.event_changed.emit(self._events)

    def load_event_templates(self) -> None:
        self._templates = list(self._template_service.get_all_templates())
        self.template_changed.emit(self._templates)

    def add_new_event(
        self, label: str, description: str, start_time: time, duration: timedelta
    ) -> None:
        if not label.strip():
            self.show_warning.emit("Название события не может быть пустым!")
            return

        event_date = date.fromisoformat(self._selected_date)
        full_start_time = datetime.combine(event_date, start_time)

        self._event_service.add_event(
            label=label,
            description=description,
            start_time=full_start_time,
            duration=duration,
        )
        self.load_events()

    def add_new_template(
        self, label: str, description: str, start_time: time, duration: timedelta
    ) -> None:
        if not label.strip():
            self.show_warning.emit("Название шаблона не может быть пустым!")
            return

        self._template_service.add_template(
            label=label,
            description=description,
            start_time=start_time,
            duration=duration,
        )
        self.load_event_templates()

    def quick_add_template(self, template: EventTemplate) -> None:
        self.add_new_event(
            label=template.label,
            description=template.description,
            start_time=template.start_time,
            duration=template.duration,
        )

    def update_event_full(self, event_id: int, label: str, description: str, start_time: datetime, duration: timedelta) -> None:
        if not label.strip():
            self.show_warning.emit("Название события не может быть пустым!")
            return
        try:
            self._event_service.update_event(
                event_id,
                label=label,
                description=description,
                start_time=start_time,
                duration=duration
            )
            self.load_events()
        except Exception as e:
            self.show_warning.emit(str(e))

    def delete_event(self, event_id: int, event_label: str, event_date_str: str) -> None:
        try:
            self._event_service.delete_event(event_id)
            self.load_events()
        except Exception as e:
            self.show_warning.emit(str(e))
