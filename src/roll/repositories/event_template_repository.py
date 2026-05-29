import logging
from datetime import time, timedelta
from typing import cast, override

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from roll.core import (
    BaseEventTemplate,
    EventTemplate,
    EventTemplateUpdateDTO,
    IEventTemplateRepository,
)
from roll.repositories.base_qsqlite_repository import BaseQtSQLiteRepository
from roll.repositories.exceptions import DTOValueError

logger = logging.getLogger(__name__)


class EventTemplateRepository(IEventTemplateRepository, BaseQtSQLiteRepository):
    def __init__(self, db: QSqlDatabase) -> None:
        """Initializes event repository with database.

        Args:
            db: QT SQL database
        """
        logger.info("Initialized event repository")
        self.db: QSqlDatabase = db

    @override
    def get(self, event_template_id: int) -> BaseEventTemplate | None:
        query = QSqlQuery(self.db)

        sql = """
        SELECT template_id, label, description, start_time, duration_seconds
        FROM event_templates
        WHERE template_id = (?);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(event_template_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.next():
            return self._build_event(query)

        return None

    @override
    def get_all(self) -> tuple[BaseEventTemplate, ...]:
        query = QSqlQuery(self.db)

        sql = """
        SELECT template_id, label, description, start_time, duration_seconds
        FROM event_templates;
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        if not query.exec():
            self._raise_on_exec(query)

        events: list[BaseEventTemplate] = []

        while query.next():
            events += [self._build_event(query)]

        return tuple(events)

    @override
    def add(self, event_template: EventTemplateUpdateDTO) -> int:
        if not (
            event_template.label
            and event_template.duration
            and event_template.start_time
            and event_template.duration.total_seconds() > 0
        ):
            raise DTOValueError

        query = QSqlQuery(self.db)

        sql = """
        INSERT INTO event_templates (label, description, start_time, duration_seconds)
        VALUES (:label, :description, :start_time, :duration_seconds);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":label", event_template.label)
        query.bindValue(":description", event_template.description)
        query.bindValue(":start_time", event_template.start_time.isoformat())
        query.bindValue(":duration_seconds", event_template.duration.total_seconds())

        if not query.exec():
            self._raise_on_exec(query)

        return cast("int", query.lastInsertId())

    @override
    def update(
        self, event_template_id: int, event_template: EventTemplateUpdateDTO
    ) -> None:
        if event_template.label == "" or (
            event_template.duration and event_template.duration.total_seconds() == 0
        ):
            raise DTOValueError

        query = QSqlQuery(self.db)

        sql = """
        UPDATE event_templates
        SET label = COALESCE(:label, label),
            description = COALESCE(:description, description),
            start_time = COALESCE(:start_time, start_time),
            duration_seconds = COALESCE(:duration_seconds, duration_seconds)
        WHERE template_id = :id;
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":label", event_template.label)
        query.bindValue(":description", event_template.description)
        query.bindValue(
            ":start_time",
            event_template.start_time.isoformat()
            if event_template.start_time
            else None,
        )
        query.bindValue(
            ":duration_seconds",
            event_template.duration.total_seconds()
            if event_template.duration
            else None,
        )
        query.bindValue(":id", event_template_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", event_template_id)

    @override
    def delete(self, event_template_id: int) -> bool:
        query = QSqlQuery(self.db)

        sql = """
        DELETE FROM event_templates
        WHERE template_id = (?)
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(event_template_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", event_template_id)
            return False

        return True

    @staticmethod
    def _build_event(query: QSqlQuery) -> BaseEventTemplate:
        e_id = cast("int", query.value(0))
        e_label = cast("str", query.value(1))
        e_desc = cast("str", query.value(2))
        e_start = cast("str", query.value(3))
        e_duration = cast("int", query.value(4))

        return EventTemplate(
            e_id,
            e_label,
            time.fromisoformat(e_start),
            timedelta(seconds=e_duration),
            e_desc,
        )
