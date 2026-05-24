import logging
from typing import override

from roll.core import (
    AttendanceStatus,
    AttendanceUpdateDTO,
    BaseAttendance,
    IAttendanceRepository,
    IAttendanceService,
    IEventRepository,
    IPersonRepository,
)
from roll.services.exceptions import (
    AttendanceNotFoundError,
    EventNotFoundError,
    PersonNotFoundError,
)

logger = logging.getLogger(__name__)


class AttendanceService(IAttendanceService):
    def __init__(
        self,
        repo: IAttendanceRepository,
        person_repo: IPersonRepository,
        event_repo: IEventRepository,
    ) -> None:
        """Initializes attendance service with attedance repository."""
        self.repo: IAttendanceRepository = repo
        self.person_repo: IPersonRepository = person_repo
        self.event_repo: IEventRepository = event_repo
        logger.info("Initialized attendance service")

    @override
    def add_attendance(
        self,
        person_id: int,
        event_id: int,
        status: AttendanceStatus = AttendanceStatus.ABSENT,
    ) -> int:

        if not self.person_repo.get(person_id):
            raise PersonNotFoundError

        if not self.event_repo.get(event_id):
            raise EventNotFoundError

        attendance = AttendanceUpdateDTO(
            person_id=person_id,
            event_id=event_id,
            status=status,
        )
        return self.repo.add(attendance)

    @override
    def get_event_attendance(self, event_id: int) -> tuple[BaseAttendance, ...]:

        if not self.event_repo.get(event_id):
            raise EventNotFoundError

        return self.repo.get_by_event(event_id)

    @override
    def get_attendance(self, attendance_id: int) -> BaseAttendance:
        attendance = self.repo.get(attendance_id)

        if attendance is None:
            raise AttendanceNotFoundError

        return attendance

    @override
    def update_attendance(self, attendance_id: int, status: AttendanceStatus) -> None:

        if not self.repo.get(attendance_id):
            raise AttendanceNotFoundError

        attendance = AttendanceUpdateDTO(status=status)
        self.repo.update(attendance_id, attendance)

    @override
    def delete_attendance(self, attendance_id: int) -> None:
        if not self.repo.delete(attendance_id):
            raise AttendanceNotFoundError
