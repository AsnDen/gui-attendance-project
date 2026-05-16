"""Attendance service for managing attendance records."""

import logging
from typing import override, Tuple
from PySide6.QtSql import QSqlQuery

from roll.core import (
    IAttendanceRepository, IAttendanceService, 
    AttendanceUpdateDTO, BaseAttendance, Attendance
)

logger = logging.getLogger(__name__)


class AttendanceService(IAttendanceService):
    def __init__(self, repo: IAttendanceRepository):
        self.repo = repo
        logger.info("Initialized attendance service")

    @override
    def mark_attendance(self, person_id: int, event_id: int) -> None:
        """Mark person as present for an event."""
        attendance = AttendanceUpdateDTO(
            person_id=person_id,
            event_id=event_id,
            status=True
        )
        self.repo.add(attendance)
        logger.info(f"Marked attendance: person {person_id} for event {event_id}")

    @override
    def get_attendance_for_event(self, event_id: int) -> Tuple[BaseAttendance, ...]:
        """Get all attendance records for an event."""
        query = QSqlQuery()
        sql = """
        SELECT attendance_id, person_id, event_id, status
        FROM attendance
        WHERE event_id = ?
        ORDER BY attendance_id
        """
        
        if not query.prepare(sql):
            logger.error(f"Failed to prepare query: {query.lastError().text()}")
            return ()
        
        query.addBindValue(event_id)
        
        if not query.exec():
            logger.error(f"Failed to execute query: {query.lastError().text()}")
            return ()
        
        records = []
        while query.next():
            record = Attendance(
                attendance_id=query.value(0),
                person_id=query.value(1),
                event_id=query.value(2),
                is_present=bool(query.value(3))
            )
            records.append(record)
        
        logger.info(f"Found {len(records)} attendance records for event {event_id}")
        return tuple(records)