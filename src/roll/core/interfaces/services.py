"""Interfaces for services.

Provides:
    IPersonService
    IEventService
    IIdentifierService
    IIdentifierReaderService
    IAttendanceService
    IVerificationService
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta
    
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
    from roll.core.entities.identifier import IdentifierType


class IPersonService(ABC):
    """Interface for managing person lifecycle."""

    @abstractmethod
    def get_person(self, person_id: int) -> BasePerson:
        """Get person by ID."""
        pass

    @abstractmethod
    def get_all_persons(self) -> tuple[BasePerson, ...]:
        """Get all persons."""
        pass

    @abstractmethod
    def add_person(self, label: str, description: str | None = None) -> int:
        """Add new person with auto-generated ID."""
        pass

    @abstractmethod
    def add_person_with_id(self, person_id: int, label: str, description: str | None = None) -> None:
        """Add new person with manual ID."""
        pass

    @abstractmethod
    def update_person(self, person_id: int, person: PersonUpdateDTO) -> None:
        """Update existing person."""
        pass

    @abstractmethod
    def delete_person(self, person_id: int) -> None:
        """Delete person."""
        pass


class IEventService(ABC):
    """Interface for managing event lifecycle."""

    @abstractmethod
    def get_event(self, event_id: int) -> BaseEvent:
        """Get event by ID."""
        pass

    @abstractmethod
    def get_all_events(self) -> tuple[BaseEvent, ...]:
        """Get all events."""
        pass

    @abstractmethod
    def add_event(self, label: str, start_time: datetime, duration: timedelta, description: str | None = None) -> int:
        """Add new event and return generated ID."""
        pass

    @abstractmethod
    def update_event(self, event_id: int, event: EventUpdateDTO) -> None:
        """Update existing event."""
        pass

    @abstractmethod
    def delete_event(self, event_id: int) -> None:
        """Delete event."""
        pass


class IIdentifierService(ABC):
    """Interface for managing identifier lifecycle."""

    @abstractmethod
    def get_identifier(self, identifier_id: int) -> BaseIdentifier:
        """Get identifier by ID."""
        pass

    @abstractmethod
    def add_identifier(self, hash_value: str, person_id: int, identifier_type: IdentifierType) -> None:
        """Add new identifier."""
        pass

    @abstractmethod
    def update_identifier(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        """Update existing identifier."""
        pass

    @abstractmethod
    def delete_identifier(self, identifier_id: int) -> None:
        """Delete identifier."""
        pass


class IIdentifierReaderService(ABC):
    """Interface for reading identifiers (QR, NFC, etc.)."""

    @abstractmethod
    def read_identifier(self) -> str:
        """Read identifier synchronously."""
        pass

    @abstractmethod
    def start_scanning(self, callback) -> None:
        """Start scanning asynchronously."""
        pass

    @abstractmethod
    def stop_scanning(self) -> None:
        """Stop scanning."""
        pass


class IAttendanceService(ABC):
    """Interface for attendance management."""

    @abstractmethod
    def mark_attendance(self, person_id: int, event_id: int) -> None:
        """Mark person as present for an event."""
        pass

    @abstractmethod
    def get_attendance_for_event(self, event_id: int) -> tuple[BaseAttendance, ...]:
        """Get all attendance records for an event."""
        pass


class IVerificationService(ABC):
    """Interface for attendance verification."""

    @abstractmethod
    def verify_hash(self, hash_value: str) -> bool:
        """Checks if hash value is stored in repository.

        If stored - returns True, else False
        """
        pass