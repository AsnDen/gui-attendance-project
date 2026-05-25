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
    )


class IPersonService(ABC):
    """Interface for managing person lifecycle."""

    @abstractmethod
    def get_person(self, person_id: int) -> BasePerson:
        """Gets person by its id.

        Args:
            person_id: valid person id.

        Returns:
            BasePerson: valid person data.

        Raises:
            PersonNotFoundError: person_id is invalid.
        """

    @abstractmethod
    def get_all_persons(self) -> tuple[BasePerson, ...]:
        """Gets all persons.

        Returns:
            tuple of BasePerson: all saved persons.
        """

    @abstractmethod
    def add_person(self, label: str, description: str) -> int:
        """Saves person data.

        Args:
            label: person label.
            description: person description.

        Returns:
            int: saved user id.

        Raises:
            EmptyLabelError: if label is empty string.
        """

    @abstractmethod
    def update_person(
        self,
        person_id: int,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> None:
        """Updates person data.

        Args:
            person_id: valid person id.
            label: person label. Not updated if None.
            description: person description. Not updated if None.

        Raises:
            EmptyLabelError: if label is empty string.
        """

    @abstractmethod
    def delete_person(self, person_id: int) -> None:
        """Deletes person.

        Args:
            person_id: valid person id.

        Raises:
            PersonNotFoundError: if label is empty string.
        """


class IEventService(ABC):
    """Interface for managing service lifecycle."""

    @abstractmethod
    def get_event(self, event_id: int) -> BaseEvent:
        pass

    @abstractmethod
    def get_all_events(self) -> tuple[BaseEvent, ...]:
        pass

    @abstractmethod
    def add_event(self, label: str, description: str | None = None) -> None:
        pass

    @abstractmethod
    def update_event(self, event_id: int, event: EventUpdateDTO) -> None:
        pass

    @abstractmethod
    def delete_event(self, event_id: int) -> None:
        pass


class IAttendanceService(ABC):
    """Interface for managing attendance lifecycle."""

    @abstractmethod
    def get_attendance(self, attendance_id: int) -> BaseAttendance:
        pass

    @abstractmethod
    def get_event_attendance(self, event_id: int) -> tuple[BaseAttendance, ...]:
        pass

    @abstractmethod
    def add_attendance(
        self, person_id: int, event_id: int, *, is_present: bool = False
    ) -> None:
        pass

    @abstractmethod
    def update_attendance(
        self, attendance_id: int, attendance: AttendanceUpdateDTO
    ) -> None:
        pass

    @abstractmethod
    def delete_attendance(self, attendance_id: int) -> None:
        pass


class IIdentifierService(ABC):
    """Interface for managing identifier lifecycle."""

    @abstractmethod
    def get_identifier(self, identifier_id: int) -> BaseIdentifier:
        pass

    @abstractmethod
    def get_person_identifiers(self, person_id: int) -> tuple[BaseIdentifier, ...]:
        pass

    @abstractmethod
    def add_identifier(self, hash_value: str, person_id: int) -> None:
        pass

    @abstractmethod
    def update_identifier(
        self, identifier_id: int, identifier: IdentifierUpdateDTO
    ) -> None:
        pass

    @abstractmethod
    def delete_identifier(self, identifier_id: int) -> None:
        pass


class IVerificationService(ABC):
    """Interface for attendance verification."""

    @abstractmethod
    def verify_hash(self, hash_value: str) -> bool:
        """Checks if hash value is stored in repository.

        If stored - returns True, else False
        """


class IIdentifierReaderService(ABC):
    """Interface for reading identifier data."""

    @abstractmethod
    def read_identifier(self) -> str | None:
        """Reads identifier data.

        Returns sha256 of data read.
        """


class ICameraAvailabilityService(ABC):
    """Interface for checking camera availability."""

    @abstractmethod
    def is_camera_available(self) -> bool:
        """Check if specified camera is available."""

    @abstractmethod
    def get_available_cameras(self) -> list[int]:
        """Get list of available camera IDs."""
