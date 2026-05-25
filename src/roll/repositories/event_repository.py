import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, cast, override

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from roll.core import Event
from roll.core.interfaces import IEventRepository
from roll.repositories.base_qsqlite_repository import BaseQtSQLiteRepository
from roll.repositories.exceptions import DTOValueError

if TYPE_CHECKING:
    from roll.core.entities import BaseEvent, EventUpdateDTO

logger = logging.getLogger(__name__)


class EventRepository(IEventRepository, BaseQtSQLiteRepository):
    def __init__(self, db: QSqlDatabase) -> None:
        """Initializes event repository with database.

        Args:
            db: QT SQL database
        """
        logger.info("Initialized event repository")
        self.db: QSqlDatabase = db

    @override
    def get(self, event_id: int) -> BaseEvent | None:
        query = QSqlQuery(self.db)

        sql = """
        SELECT event_id, label, description, start_time, duration_seconds
        FROM events
        WHERE event_id = (?);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(event_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.next():
            return self._build_event(query)

        return None

    @override
    def get_all(self) -> tuple[BaseEvent, ...]:
        query = QSqlQuery(self.db)

        sql = """
        SELECT event_id, label, description, start_time, duration_seconds
        FROM events;
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        if not query.exec():
            self._raise_on_exec(query)

        events: list[BaseEvent] = []

        while query.next():
            events += [self._build_event(query)]

        return tuple(events)

    @override
    def add(self, event: EventUpdateDTO) -> int:
        if not (
            event.label
            and event.duration
            and event.start_time
            and event.duration.total_seconds() > 0
        ):
            raise DTOValueError

        query = QSqlQuery(self.db)

        sql = """
        INSERT INTO events (label, description, start_time, duration_seconds)
        VALUES (:label, :description, :start_time, :duration_seconds);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":label", event.label)
        query.bindValue(":description", event.description)
        query.bindValue(":start_time", event.start_time.isoformat())
        query.bindValue(":duration_seconds", event.duration.total_seconds())

        if not query.exec():
            self._raise_on_exec(query)

        return cast("int", query.lastInsertId())

    @override
    def update(self, event_id: int, event: EventUpdateDTO) -> None:
        if event.label == "" or (
            event.duration and event.duration.total_seconds() == 0
        ):
            raise DTOValueError

        query = QSqlQuery(self.db)

        sql = """
        UPDATE events
        SET label = COALESCE(:label, label),
            description = COALESCE(:description, description),
            start_time = COALESCE(:start_time, start_time),
            duration_seconds = COALESCE(:duration_seconds, duration_seconds)
        WHERE event_id = :id;
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":label", event.label)
        query.bindValue(":description", event.description)
        query.bindValue(
            ":start_time", event.start_time.isoformat() if event.start_time else None
        )
        query.bindValue(
            ":duration_seconds",
            event.duration.total_seconds() if event.duration else None,
        )
        query.bindValue(":id", event_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", event_id)

    @override
    def delete(self, event_id: int) -> bool:
        query = QSqlQuery(self.db)

        sql = """
        DELETE FROM events
        WHERE event_id = (?)
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(event_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", event_id)
            return False

        return True

    @staticmethod
    def _build_event(query: QSqlQuery) -> BaseEvent:
        e_id = cast("int", query.value(0))
        e_label = cast("str", query.value(1))
        e_desc = cast("str", query.value(2))
        e_start = cast("str", query.value(3))
        e_duration = cast("int", query.value(4))

        return Event(
            e_id,
            e_label,
            datetime.fromisoformat(e_start),
            timedelta(seconds=e_duration),
            e_desc,
        )
