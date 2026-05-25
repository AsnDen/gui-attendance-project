from abc import ABC, abstractmethod
from datetime import time, timedelta

from PySide6.QtCore import QDate, SignalInstance

from roll.core import BaseEvent, EventTemplate


class ICalendarPanelViewModel(ABC):
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

    event_changed: SignalInstance
    template_changed: SignalInstance
    show_warning: SignalInstance
    show_success: SignalInstance
    date_changed: SignalInstance

    @property
    @abstractmethod
    def events(self) -> list[BaseEvent]:
        """Gets all events for selected date.

        Returns:
            List of BaseEvent: all events for the selected date.
        """

    @property
    @abstractmethod
    def templates(self) -> list[EventTemplate]:
        """Gets all available event templates.

        Returns:
            list[EventTemplate]: A list of event templates for the quick-add panel.
        """

    @property
    @abstractmethod
    def selected_date(self) -> str:
        """Gets selected date.

        Returns:
            str: date in format yyyy-MM-dd.
        """

    @abstractmethod
    def load_events(self) -> None:
        """Loads events from the event service.

        Triggers the `event_changed` signal once data fetching and
        filtering are complete.
        """

    @abstractmethod
    def load_event_templates(self) -> None:
        """Loads event templates from the event tepmlate service.

        Triggers the `template_changed` signal once data fetching and
        filtering are complete.
        """

    @abstractmethod
    def select_date(self, date: QDate) -> None:
        """Handles the date selection event from the calendar widget.

        Updates the internal state and emits the `date_changed` signal.

        Args:
            date: The date object selected by the user in the UI.
        """

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def quick_add_template(self, template: EventTemplate) -> None:
        """Quickly adds an existing event to the selected date.

        Used when double-clicking an item in the "Event template" list.

        Args:
            template: The EventTemplate object selected from the templates list.
        """
