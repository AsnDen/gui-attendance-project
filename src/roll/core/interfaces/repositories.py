"""Interfaces for repositories.

Provides:
    IAttendanceRepository,
    IEventRepository,
    IIdentifierRepository
    IPersonRepository,
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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
        """Finds and returns attendance by it's id.

        Returns None if attendance is not found.

        Args:
            attendance_id: id of an attendance
        """

    @abstractmethod
    def add(self, attendance: AttendanceUpdateDTO) -> None:
        """Saves new attendance in repository.

        Args:
            attendance: All DTO fields of attendance must not be None
        """

    @abstractmethod
    def update(self, attendance_id: int, attendance: AttendanceUpdateDTO) -> None:
        """Updates existing attendance info.

        Args:
            attendance_id: id of an attendance
            attendance: DTO with fields that may be empty.
        """

    @abstractmethod
    def delete(self, attendance_id: int) -> bool:
        """Deletes attendance from repository.

        Returns bool if operation is successfull.

        Args:
            attendance_id: id of an attendance
        """


class IEventRepository(ABC):
    """Interface for event repository."""

    @abstractmethod
    def get(self, event_id: int) -> BaseEvent | None:
        """Finds and returns event by it's id.

        Returns None if event is not found.
        """

    @abstractmethod
    def get_all(self) -> tuple[BaseEvent, ...]:
        """Returns tuple of all saved event."""

    @abstractmethod
    def add(self, event: EventUpdateDTO) -> None:
        """Saves new event in repository."""

    @abstractmethod
    def update(self, event_id: int, event: EventUpdateDTO) -> None:
        """Updates existing event info."""

    @abstractmethod
    def delete(self, event_id: int) -> bool:
        """Deletes event from repository.

        Returns bool if operation is successfull.
        """


class IPersonRepository(ABC):
    """Interface for person repository."""

    @abstractmethod
    def get(self, person_id: int) -> BasePerson | None:
        """Finds and returns person by it's id.

        Returns:
            None if person is not found.
            BasePerson if person is found.
        """

    @abstractmethod
    def get_all(self) -> tuple[BasePerson, ...]:
        """Finds all persons saved in repository.

        Returns:
            tuple: all saved persons.
        """

    @abstractmethod
    def add(self, person: PersonUpdateDTO) -> int:
        """Saves new person in repository.

        Args:
            person: DTO with non-empty fields.

        Returns:
            int: id of inserted data.
        """

    @abstractmethod
    def update(self, person_id: int, person: PersonUpdateDTO) -> None:
        """Updates person info.

        Args:
            person_id: id of person.
            person: DTO with fields that may be empty.
        """

    @abstractmethod
    def delete(self, person_id: int) -> bool:
        """Deletes person from repository.

        Args:
            person_id: id of person.

        Returns:
            bool: if operation is successfull or not.
        """


class IIdentifierRepository(ABC):
    """Interface for identifier repository."""

    @abstractmethod
    def get(self, identifier_id: int) -> BaseIdentifier | None:
        """Finds and returns identifier by it's id.

        Returns None if identifier is not found.
        """

    @abstractmethod
    def add(self, identifier: IdentifierUpdateDTO) -> None:
        """Saves new identifier in repository."""

    @abstractmethod
    def update(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        """Updates existing identifier info."""

    @abstractmethod
    def delete(self, identifier_id: int) -> bool:
        """Deletes identifier from repository.

        Returns bool if operation is successfull.
        """
