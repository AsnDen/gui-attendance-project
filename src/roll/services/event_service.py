import logging
from datetime import datetime, timedelta
from typing import override

from roll.core import BaseEvent, IEventRepository, IEventService, EventUpdateDTO
from roll.services.exceptions import EventNotFoundError, EmptyLabelError, InvalidDurationError

logger = logging.getLogger(__name__)


class EventService(IEventService):
    def __init__(self, repo: IEventRepository) -> None:
        self.repo: IEventRepository = repo
        logger.info("Initialized event service")

    @override
    def add_event(self, label: str, start_time: datetime, duration: timedelta, description: str | None = None) -> int:
        if not label or not label.strip():
            raise EmptyLabelError("Event label cannot be empty")
        if duration.seconds <= 0:
            raise InvalidDurationError("Duration must be positive")

        event = EventUpdateDTO(label=label.strip(), start_time=start_time, duration=duration, description=description)
        event_id = self.repo.add(event)
        logger.info(f"Added event: {label} with ID: {event_id}")
        return event_id

    @override
    def get_event(self, event_id: int) -> BaseEvent:
        event = self.repo.get(event_id)
        if event is None:
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        return event

    @override
    def get_all_events(self) -> tuple[BaseEvent, ...]:
        return self.repo.get_all()

    @override
    def update_event(self, event_id: int, event: EventUpdateDTO) -> None:
        self.repo.update(event_id, event)
        logger.info(f"Updated event {event_id}")

    @override
    def delete_event(self, event_id: int) -> None:
        if not self.repo.delete(event_id):
            raise EventNotFoundError(f"Event with ID {event_id} not found")
        logger.info(f"Deleted event {event_id}")