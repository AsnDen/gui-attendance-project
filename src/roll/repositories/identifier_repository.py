import logging
from typing import TYPE_CHECKING, cast, override, Tuple

from PySide6.QtSql import QSqlQuery

from roll.core import IdentifierType, IIdentifierRepository
from roll.repositories.base_qsqlite_repository import BaseQtSQLiteRepository
from roll.repositories.exceptions import DTOValueError

if TYPE_CHECKING:
    from roll.core.entities import BaseIdentifier, IdentifierUpdateDTO

logger = logging.getLogger(__name__)


class IdentifierRepository(IIdentifierRepository, BaseQtSQLiteRepository):
    def __init__(self) -> None:
        logger.info("Initialized identifier repository")

    @override
    def get(self, identifier_id: int) -> BaseIdentifier | None:
        query = QSqlQuery()
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
    def get_by_hash(self, hash_value: str) -> BaseIdentifier | None:
        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE hash_value = (?);
        """
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.addBindValue(hash_value)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        if query.next():
            return self._build_identifier(query)
        return None

    @override
    def get_by_person(self, person_id: int) -> Tuple[BaseIdentifier, ...]:
        """Get all identifiers for a person."""
        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE person_id = (?)
        ORDER BY identifier_id;
        """
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.addBindValue(person_id)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        identifiers = []
        while query.next():
            identifiers.append(self._build_identifier(query))
        
        logger.info(f"Found {len(identifiers)} identifiers for person {person_id}")
        return tuple(identifiers)

    @override
    def add(self, identifier: IdentifierUpdateDTO) -> None:
        if not (identifier.hash_value and identifier.person_id and identifier.identifier_type):
            raise DTOValueError("Missing required identifier fields")
        
        query = QSqlQuery()
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
            error_text = query.lastError().text()
            logger.error(f"Failed to add identifier: {error_text}")
            raise Exception(f"Database error: {error_text}")
        
        logger.info(f"Added identifier for person {identifier.person_id}")

    @override
    def update(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        if not (identifier.hash_value and identifier.person_id and identifier.identifier_type):
            raise DTOValueError
        
        query = QSqlQuery()
        sql = """
        UPDATE identifiers
        SET hash_value = CASE
                WHEN :hash_value = '' THEN NULL
                WHEN :hash_value IS NULL THEN hash_value
                ELSE :hash_value
            END,
            person_id = COALESCE(:person_id, person_id),
            identifier_type = COALESCE(:identifier_type, identifier_type)
        WHERE identifier_id = :id;
        """
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.bindValue("person_id", identifier.person_id)
        query.bindValue("hash_value", identifier.hash_value)
        query.bindValue("identifier_type", identifier.identifier_type.name)
        query.bindValue("id", identifier_id)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", identifier_id)

    @override
    def delete(self, identifier_id: int) -> bool:
        query = QSqlQuery()
        sql = "DELETE FROM identifiers WHERE identifier_id = (?)"
        
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
        
        return i_type.value(i_id, i_person_id, i_hash)