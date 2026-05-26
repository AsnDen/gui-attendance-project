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
    """Interface for the CalendarPanel view model.

    Attributes:
        event_changed (Signal): Emitted when the list of events is
            updated. Passes a list of BaseEvent to the slot.
        template_changed (Signal): Emitted when the list of available event
            templates is updated. Passes a list of EventTemplate
            objects (list[EventTemplate]).
        show_warning (Signal): Emitted when a business logic error or warning
            occurs. Passes a string message (str) to be displayed in the UI.
        show_success (Signal): Emitted upon successful completion of an operation.
            Passes a string message (str) to be displayed in the UI.
        date_changed (Signal): Emitted when the currently selected date changes.
            Passes the date string (str) in "yyyy-MM-dd" format.
    """

    event_changed: Signal = Signal(list)
    template_changed: Signal = Signal(list)
    show_warning: Signal = Signal(str)
    show_success: Signal = Signal(str)
    date_changed: Signal = Signal(str)

    def __init__(
        self, event_serivce: IEventService, template_service: IEventTemplateService
    ) -> None:
        super().__init__()
        self._event_service: IEventService = event_serivce
        self._template_serivce: IEventTemplateService = template_service

        self._events: list[BaseEvent] = []
        self._templates: list[BaseEventTemplate] = []
        self._selected_date: str = datetime.now(tz=UTC).date().isoformat()

    @property
    def events(self) -> list[BaseEvent]:
        """Gets all events for selected date.

        Returns:
            List of BaseEvent: all events for the selected date.
        """
        return self._events

    @property
    def templates(self) -> list[BaseEventTemplate]:
        """Gets all available event templates.

        Returns:
            list[EventTemplate]: A list of event templates for the quick-add panel.
        """
        return self._templates

    @property
    def selected_date(self) -> str:
        """Gets selected date.

        Returns:
            str: date in format yyyy-MM-dd.
        """
        return self._selected_date

    def select_date(self, date: QDate) -> None:
        """Loads events from the event service.

        Triggers the `event_changed` signal once data fetching and
        filtering are complete.
        """
        new_date_str = date.toString("yyyy-MM-dd")
        if self._selected_date != new_date_str:
            self._selected_date = new_date_str
            self.date_changed.emit(self._selected_date)

    def load_events(self) -> None:
        """Loads event templates from the event tepmlate service.

        Triggers the `template_changed` signal once data fetching and
        filtering are complete.
        raise NotImplementedError
        """
        current_date = date.fromisoformat(self._selected_date)
        self._events = list(self._event_service.get_day_events(current_date))
        self.event_changed.emit(self._events)

    def load_event_templates(self) -> None:
        """Handles the date selection event from the calendar widget.

        Updates the internal state and emits the `date_changed` signal.

        Args:
            date: The date object selected by the user in the UI.
        """
        self._templates = list(self._template_serivce.get_all_templates())
        self.template_changed.emit(self._templates)

    def add_new_event(
        self, label: str, description: str, start_time: time, duration: timedelta
    ) -> None:
        """Adds new event to the currently selected date.

        This method validates the input, creates a new schedule item,
        saves it to the database, and notifies the UI about the updates.

        Args:
            label: The name of the new event. Must not be empty.
            description: The description of event. Can be an empty string.
            start_time: The event start time.
            duration: The event duration.
        """
        if not label.strip():
            self.show_warning.emit("Название события не может быть пустым!")
            return

        event_date = date.fromisoformat(self._selected_date)
        full_start_time = datetime.combine(event_date, start_time)

        _ = self._event_service.add_event(
            label=label,
            description=description,
            start_time=full_start_time,
            duration=duration,
        )

        self.show_success.emit(f"Предмет '{label}' успешно добавлен!")
        self.load_events()

    def add_new_template(
        self, label: str, description: str, start_time: time, duration: timedelta
    ) -> None:
        """Creates a new reusable event template using event template service.

        Args:
            label: The name of the template. Must not be empty.
            description: Default description for events created via this template.
            start_time: Default start time for this template.
            duration: Default duration for this template.
        """
        if not label.strip():
            self.show_warning.emit("Название шаблона не может быть пустым!")
            return

        _ = self._template_serivce.add_template(
            label=label,
            description=description,
            start_time=start_time,
            duration=duration,
        )
        self.show_success.emit(f"Шаблон '{label}' успешно создан!")
        self.load_event_templates()

    def quick_add_template(self, template: EventTemplate) -> None:
        """Quickly adds an existing event to the selected date.

        Used when double-clicking an item in the "Event template" list.

        Args:
            template: The EventTemplate object selected from the templates list.
        """
        self.add_new_event(
            label=template.label,
            description=template.description,
            start_time=template.start_time,
            duration=template.duration,
        )
