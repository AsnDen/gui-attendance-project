import logging
from datetime import date
from typing import TYPE_CHECKING, override

from roll.core import BaseEvent, EventUpdateDTO, IEventRepository, IEventService
from roll.services.exceptions import (
    EmptyLabelError,
    EventNotFoundError,
    ZeroDurationError,
)

if TYPE_CHECKING:
    from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EventService(IEventService):
    def __init__(self, repo: IEventRepository) -> None:
        """Initializes event service with event repository."""
        self.repo: IEventRepository = repo
        logger.info("Initialized event service")

    @override
    def add_event(
        self,
        label: str,
        start_time: datetime,
        duration: timedelta,
        description: str = "",
    ) -> int:
        if label == "":
            raise EmptyLabelError

        if duration.total_seconds() == 0:
            raise ZeroDurationError

        event = EventUpdateDTO(
            label=label,
            start_time=start_time,
            duration=duration,
            description=description,
        )
        return self.repo.add(event)

    @override
    def get_event(self, event_id: int) -> BaseEvent:
        event = self.repo.get(event_id)

        if event is None:
            raise EventNotFoundError

        return event

    @override
    def get_all_events(self) -> tuple[BaseEvent, ...]:
        return self.repo.get_all()

    # TODO (asnden): REDO THIS
    @override
    def get_day_events(self, date: date) -> tuple[BaseEvent, ...]:
        events = self.repo.get_all()
        ans: list[BaseEvent] = []
        for event in events:
            if event.start_time.date() == date:
                ans += [event]
        return tuple(ans)

    @override
    def update_event(
        self,
        event_id: int,
        *,
        label: str | None = None,
        start_time: datetime | None = None,
        duration: timedelta | None = None,
        description: str | None = None,
    ) -> None:
        if label == "":
            raise EmptyLabelError

        if duration is not None and duration.total_seconds() == 0:
            raise ZeroDurationError

        event = EventUpdateDTO(
            label=label,
            start_time=start_time,
            duration=duration,
            description=description,
        )
        self.repo.update(event_id, event)

    @override
    def delete_event(self, event_id: int) -> None:
        if not self.repo.delete(event_id):
            raise EventNotFoundError
