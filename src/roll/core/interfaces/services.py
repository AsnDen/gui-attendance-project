from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from roll.core import BaseEventTemplate
from roll.core.entities import AttendanceStatus

if TYPE_CHECKING:
    from roll.core.entities import (
        BaseAttendance,
        BaseEvent,
        BaseIdentifier,
        BasePerson,
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
            int: saved person id.

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
        """Gets event by its id.

        Args:
            event_id: valid event id.

        Returns:
            BaseEvent: valid event data.

        Raises:
            EventNotFoundError: event_id is invalid.
        """

    @abstractmethod
    def get_all_events(self) -> tuple[BaseEvent, ...]:
        """Gets all events.

        Returns:
            tuple of BaseEvent: all saved events.
        """

    @abstractmethod
    def get_day_events(self, date: date) -> tuple[BaseEvent, ...]:
        pass

    @abstractmethod
    def add_event(
        self,
        label: str,
        start_time: datetime,
        duration: timedelta,
        description: str = "",
    ) -> int:
        """Saves event data.

        Args:
            label: event label.
            start_time: event start time.
            duration: event duration.
            description: event description.

        Returns:
            int: saved event id.

        Raises:
            EmptyLabelError: if label is empty string.
            ZeroDurationError: if duration.total_seconds() == 0
        """

    @abstractmethod
    def update_event(
        self,
        event_id: int,
        *,
        label: str | None = None,
        start_time: datetime | None = None,
        duration: timedelta | None = None,
        description: str | None = None,
    ) -> None:
        """Updates event data.

        Args:
            event_id: valid event id.
            label: event label. Not updated if None.
            start_time: event start time. Not updated if None.
            duration: event duration. Not updated if None.
            description: event description. Not updated if None.

        Raises:
            EmptyLabelError: if label is empty string.
            ZeroDurationError: if duration.total_seconds() == 0
        """

    @abstractmethod
    def delete_event(self, event_id: int) -> None:
        """Deletes event.

        Args:
            event_id: valid event id.

        Raises:
            EventNotFoundError: event_id is invalid.
        """


class IEventTemplateService(ABC):
    @abstractmethod
    def get_template(self, event_template_id: int) -> BaseEventTemplate:
        pass

    @abstractmethod
    def get_all_templates(self) -> tuple[BaseEventTemplate, ...]:
        pass

    @abstractmethod
    def add_template(
        self,
        label: str,
        start_time: time,
        duration: timedelta,
        description: str = "",
    ) -> int:
        pass

    @abstractmethod
    def update_template(
        self,
        event_template_id: int,
        *,
        label: str | None = None,
        start_time: time | None = None,
        duration: timedelta | None = None,
        description: str | None = None,
    ) -> None:
        pass

    @abstractmethod
    def delete_template(self, event_template_id: int) -> None:
        pass


class IAttendanceService(ABC):
    """Interface for managing attendance lifecycle."""

    @abstractmethod
    def get_attendance(self, attendance_id: int) -> BaseAttendance:
        """Gets attendance by its id.

        Args:
            attendance_id: valid attendance id.

        Returns:
            BaseAttendance: valid attendance data.

        Raises:
            AttendanceNotFoundError: attendance_id is invalid.
        """

    @abstractmethod
    def get_event_attendance(self, event_id: int) -> tuple[BaseAttendance, ...]:
        """Gets attendances by event id.

        Args:
            event_id: valid event id.

        Returns:
            tuple of BaseAttendance: valid attendance data.

        Raises:
            EventNotFoundError: event_id is invalid.
        """

    @abstractmethod
    def add_attendance(
        self,
        person_id: int,
        event_id: int,
        status: AttendanceStatus = AttendanceStatus.ABSENT,
    ) -> int:
        """Saves attendance data.

        Args:
            person_id: id of person who attend event.
            event_id: if of event.
            status: attendance status.

        Returns:
            int: saved attendance id.

        Raises:
            PersonNotFoundError: if person does not exist.
            EventNotFoundError: if event does not exist.
        """

    @abstractmethod
    def update_attendance(self, attendance_id: int, status: AttendanceStatus) -> None:
        """Updates attendance data.

        Args:
            attendance_id: valid attendance id.
            status: new attendance status.

        Raises:
            AttendanceNotFoundError: if attendance_id is invalid.
        """

    @abstractmethod
    def delete_attendance(self, attendance_id: int) -> None:
        """Deletes attendance.

        Args:
            attendance_id: valid attendance id.

        Raises:
            AttendanceNotFoundError: attendance_id is invalid.
        """


class IIdentifierService(ABC):
    """Interface for managing identifier lifecycle."""

    @abstractmethod
    def get_identifier(self, identifier_id: int) -> BaseIdentifier:
        """Gets identifier by its id.

        Args:
            identifier_id: valid identigier id.

        Returns:
            BaseIdentifier: valid identifier data.

        Raises:
            IdentifierNotFoundError: identigier_id is invalid.
        """

    @abstractmethod
    def get_person_identifiers(self, person_id: int) -> tuple[BaseIdentifier, ...]:
        """Gets identifiers by person id.

        Args:
            person_id: valid person id.

        Returns:
            tuple of BaseIdentifier: valid identifier data.

        Raises:
            PersonNotFoundError: person_id is invalid.
        """

    @abstractmethod
    def add_identifier(self, hash_value: str, person_id: int) -> int:
        """Saves identifier data.

        Args:
            hash_value: encrypted value of data.
            person_id: id of person who owns identifier.

        Returns:
            int: saved attendance id.

        Raises:
            PersonNotFoundError: if person does not exist.
        """

    @abstractmethod
    def update_identifier(self, identifier_id: int, hash_value: str) -> None:
        """Updates identifier data.

        Args:
            identifier_id: valid identifier id.
            hash_value: new hash value.

        Raises:
            IdentifierNotFoundError: if identifier_id is invalid.
        """

    @abstractmethod
    def delete_identifier(self, identifier_id: int) -> None:
        """Deletes identifier.

        Args:
            identifier_id: valid identifier id.

        Raises:
            identifierNotFoundError: identifier_id is invalid.
        """


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
    def read_identifier(self) -> str:
        """Reads identifier data.

        Returns sha256 of data read.
        """
