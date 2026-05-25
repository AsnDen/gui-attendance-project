"""Classes for entities.

Provides:
    AttendanceShema, BaseAttendance,
    Attendance, AttendanceUpdateDTO for attendance data.

    EventShema, BaseEvent,
    Event, EventUpdateDTO for event data.

    IdentifierShema, BaseIdentifier,
    Identifier, IdentifierUpdateDTO for identifier data.

    PersonShema, BasePerson,
    Person, PersonUpdateDTO for person data.
"""

from roll.core.entities.attendance import (
    Attendance,
    AttendanceShema,
    AttendanceStatus,
    AttendanceUpdateDTO,
    BaseAttendance,
)
from roll.core.entities.event import (
    BaseEvent,
    BaseEventTemplate,
    Event,
    EventShema,
    EventTemplate,
    EventTemplateShema,
    EventTemplateUpdateDTO,
    EventUpdateDTO,
)
from roll.core.entities.identifier import (
    BaseIdentifier,
    CardIdentifier,
    IdentifierShema,
    IdentifierType,
    IdentifierUpdateDTO,
    QRIdentifier,
)
from roll.core.entities.person import BasePerson, Person, PersonShema, PersonUpdateDTO

__all__ = [
    "Attendance",
    "AttendanceShema",
    "AttendanceStatus",
    "AttendanceUpdateDTO",
    "BaseAttendance",
    "BaseEvent",
    "BaseEventTemplate",
    "BaseIdentifier",
    "BasePerson",
    "CardIdentifier",
    "Event",
    "EventShema",
    "EventTemplate",
    "EventTemplateShema",
    "EventTemplateUpdateDTO",
    "EventUpdateDTO",
    "IdentifierShema",
    "IdentifierType",
    "IdentifierUpdateDTO",
    "Person",
    "PersonShema",
    "PersonUpdateDTO",
    "QRIdentifier",
]
