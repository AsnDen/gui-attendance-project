import logging
from typing import override

from roll.core import (
    AttendanceUpdateDTO,
    BaseAttendance,
    IAttendanceRepository,
    IAttendanceService,
)
from roll.services.exceptions import AttendanceNotFoundError

logger = logging.getLogger(__name__)


class AttendanceService(IAttendanceService):
    def __init__(self, repo: IAttendanceRepository) -> None:
        """Initializes attendance service with attendance repository.

        Sends log message on init end
        """
        self.repo: IAttendanceRepository = repo
        logger.info("Initialized attendance service")

    @override
    def add_attendance(
        self, person_id: int, event_id: int, *, is_present: bool = False
    ) -> None:
        attendance = AttendanceUpdateDTO(
            person_id=person_id,
            event_id=event_id,
            status=is_present,
        )
        self.repo.add(attendance)

    @override
    def get_event_attendance(self, event_id: int) -> tuple[BaseAttendance, ...]:
        pass

    @override
    def get_attendance(self, attendance_id: int) -> BaseAttendance:
        attendance = self.repo.get(attendance_id)

        if attendance is None:
            raise AttendanceNotFoundError

        return attendance

    @override
    def update_attendance(
        self, attendance_id: int, attendance: AttendanceUpdateDTO
    ) -> None:
        self.repo.update(attendance_id, attendance)

    @override
    def delete_attendance(self, attendance_id: int) -> None:
        if not self.repo.delete(attendance_id):
            raise AttendanceNotFoundError
