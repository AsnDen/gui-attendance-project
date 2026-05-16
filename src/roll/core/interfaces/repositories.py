"""Interfaces for repositories.

Provides:
    IAttendanceRepository,
    IEventRepository,
    IIdentifierRepository
    IPersonRepository,
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from roll.core.entities import (
        AttendanceUpdateDTO,
        BaseAttendance,
        BaseEvent,
        BaseIdentifier,
        BasePerson,
        EventUpdateDTO,
        IdentifierUpdateDTO,
        PersonUpdateDTO,
    )


class IAttendanceRepository(ABC):
    """Interface for attendance repository."""

    @abstractmethod
    def get(self, attendance_id: int) -> BaseAttendance | None:
        """Finds and returns attendance by it's id."""

    @abstractmethod
    def get_by_event(self, event_id: int) -> Tuple[BaseAttendance, ...]:
        """Get all attendance records for an event."""
        pass

    @abstractmethod
    def add(self, attendance: AttendanceUpdateDTO) -> None:
        """Saves new attendance in repository."""

    @abstractmethod
    def update(self, attendance_id: int, attendance: AttendanceUpdateDTO) -> None:
        """Updates existing attendance info."""

    @abstractmethod
    def delete(self, attendance_id: int) -> bool:
        """Deletes attendance from repository."""


class IEventRepository(ABC):
    """Interface for event repository."""

    @abstractmethod
    def get(self, event_id: int) -> BaseEvent | None:
        """Finds and returns event by it's id."""

    @abstractmethod
    def get_all(self) -> tuple[BaseEvent, ...]:
        """Returns tuple of all saved events."""

    @abstractmethod
    def add(self, event: EventUpdateDTO) -> int:
        """Saves new event in repository and returns generated ID."""

    @abstractmethod
    def update(self, event_id: int, event: EventUpdateDTO) -> None:
        """Updates existing event info."""

    @abstractmethod
    def delete(self, event_id: int) -> bool:
        """Deletes event from repository."""


class IPersonRepository(ABC):
    """Interface for person repository."""

    @abstractmethod
    def get(self, person_id: int) -> BasePerson | None:
        pass

    @abstractmethod
    def get_all(self) -> tuple[BasePerson, ...]:
        pass

    @abstractmethod
    def add(self, person: PersonUpdateDTO) -> int:
        """Saves new person with auto-generated ID and returns ID."""
        pass

    @abstractmethod
    def add_with_id(self, person_id: int, label: str, description: str | None = None) -> None:
        """Saves new person with manual ID."""
        pass

    @abstractmethod
    def update(self, person_id: int, person: PersonUpdateDTO) -> None:
        pass

    @abstractmethod
    def delete(self, person_id: int) -> bool:
        pass


class IIdentifierRepository(ABC):
    """Interface for identifier repository."""

    @abstractmethod
    def get(self, identifier_id: int) -> BaseIdentifier | None:
        """Finds and returns identifier by it's id."""

    @abstractmethod
    def get_by_hash(self, hash_value: str) -> BaseIdentifier | None:
        """Finds and returns identifier by hash value."""

    @abstractmethod
    def get_by_person(self, person_id: int) -> Tuple[BaseIdentifier, ...]:
        """Get all identifiers for a person."""
        pass

    @abstractmethod
    def add(self, identifier: IdentifierUpdateDTO) -> None:
        """Saves new identifier in repository."""

    @abstractmethod
    def update(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        """Updates existing identifier info."""

    @abstractmethod
    def delete(self, identifier_id: int) -> bool:
        """Deletes identifier from repository."""