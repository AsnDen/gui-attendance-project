"""Classes for event objects.

Provides:
    EventShema: base fields of event objects.
    BaseEvent: base class for event.
    Event: event object.
    EventUpdateDTO: DTO for event object.
"""

from abc import ABC
from dataclasses import dataclass
from datetime import (  # noqa: TC003 # for pytest to work properly
    datetime,
    time,
    timedelta,
)


@dataclass(frozen=True)
class EventShema:
    """Represents event fields."""

    label: str | None = None
    start_time: datetime | None = None
    duration: timedelta | None = None
    description: str | None = None


@dataclass(frozen=True)
class EventTemplateShema:
    """Represents event template fields."""

    label: str | None = None
    start_time: time | None = None
    duration: timedelta | None = None
    description: str | None = None


@dataclass(frozen=True)
class EventUpdateDTO(EventShema):
    """Data transfer object for event."""


@dataclass(frozen=True)
class EventTemplateUpdateDTO(EventTemplateShema):
    """Data transfer object for event template."""


@dataclass
class BaseEvent(ABC):
    """Represents base event info."""

    event_id: int
    label: str
    start_time: datetime
    duration: timedelta
    description: str = ""


@dataclass
class BaseEventTemplate(ABC):
    """Represents base event template info."""

    event_id: int
    label: str
    start_time: time
    duration: timedelta
    description: str = ""


class Event(BaseEvent):
    """Represents event info."""


class EventTemplate(BaseEventTemplate):
    """Represents event template info."""
