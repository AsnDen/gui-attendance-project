import logging
from typing import TYPE_CHECKING, cast, override

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from roll.core import IdentifierType, IIdentifierRepository
from roll.repositories.base_qsqlite_repository import BaseQtSQLiteRepository
from roll.repositories.exceptions import DTOValueError

if TYPE_CHECKING:
    from roll.core.entities import BaseIdentifier, IdentifierUpdateDTO

logger = logging.getLogger(__name__)


class IdentifierRepository(IIdentifierRepository, BaseQtSQLiteRepository):
    def __init__(self, db: QSqlDatabase) -> None:
        """Initializes identifier repository with database.

        Args:
            db: QT SQL database
        """
        logger.info("Initialized identifier repository")
        self.db: QSqlDatabase = db

    @override
    def get(self, identifier_id: int) -> BaseIdentifier | None:
        query = QSqlQuery(self.db)

        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE identifier_id = (?);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(identifier_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.next():
            return self._build_identifier(query)

        return None

    @override
    def get_by_person(self, person_id: int) -> tuple[BaseIdentifier, ...]:
        query = QSqlQuery(self.db)

        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE person_id = (?);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(person_id)

        if not query.exec():
            self._raise_on_exec(query)

        identifiers: list[BaseIdentifier] = []
        while query.next():
            identifiers += [self._build_identifier(query)]

        return tuple(identifiers)

    @override
    def add(self, identifier: IdentifierUpdateDTO) -> int:
        if not (
            identifier.hash_value
            and identifier.person_id
            and identifier.identifier_type
        ):
            raise DTOValueError

        query = QSqlQuery(self.db)

        sql = """
        INSERT INTO identifiers (person_id, hash_value, identifier_type)
        VALUES (:person_id, :hash_value, :identifier_type);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":person_id", identifier.person_id)
        query.bindValue(":hash_value", identifier.hash_value)
        query.bindValue(":identifier_type", identifier.identifier_type.name)

        if not query.exec():
            self._raise_on_exec(query)

        return cast("int", query.lastInsertId())

    @override
    def update(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        query = QSqlQuery(self.db)

        sql = """
        UPDATE identifiers
        SET
            hash_value = COALESCE(:hash_value, hash_value),
            person_id = COALESCE(:person_id, person_id),
            identifier_type = COALESCE(:identifier_type, identifier_type)
        WHERE identifier_id = :id;
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.bindValue(":person_id", identifier.person_id)
        query.bindValue(":hash_value", identifier.hash_value)
        query.bindValue(
            ":identifier_type",
            identifier.identifier_type.name if identifier.identifier_type else None,
        )
        query.bindValue(":id", identifier_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", identifier_id)

    @override
    def delete(self, identifier_id: int) -> bool:
        query = QSqlQuery(self.db)

        sql = """
        DELETE FROM identifiers
        WHERE identifier_id = (?);
        """

        if not query.prepare(sql):
            self._raise_on_prepare(query)

        query.addBindValue(identifier_id)

        if not query.exec():
            self._raise_on_exec(query)

        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", identifier_id)
            return False

        return True

    @staticmethod
    def _build_identifier(query: QSqlQuery) -> BaseIdentifier:
        i_id = cast("int", query.value(0))
        i_hash = cast("str", query.value(1))
        i_person_id = cast("int", query.value(2))
        i_type = IdentifierType[cast("str", query.value(3))]

        return i_type.value(
            i_id,
            i_person_id,
            i_hash,
        )
