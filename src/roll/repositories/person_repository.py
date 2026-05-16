import logging
from typing import cast, override

from PySide6.QtSql import QSqlQuery

from roll.core import BasePerson, IPersonRepository, Person, PersonUpdateDTO
from roll.repositories.base_qsqlite_repository import BaseQtSQLiteRepository
from roll.repositories.exceptions import DTOValueError

logger = logging.getLogger(__name__)


class PersonRepository(IPersonRepository, BaseQtSQLiteRepository):
    def __init__(self) -> None:
        logger.info("Initialized person repository")

    @override
    def get(self, person_id: int) -> BasePerson | None:
        query = QSqlQuery()
        sql = "SELECT person_id, label, description FROM persons WHERE person_id = ?;"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.addBindValue(person_id)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        if query.next():
            return self._build_person(query)
        return None

    @override
    def get_all(self) -> tuple[BasePerson, ...]:
        query = QSqlQuery()
        sql = "SELECT person_id, label, description FROM persons ORDER BY person_id;"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        persons: list[BasePerson] = []
        while query.next():
            person = self._build_person(query)
            if person:
                persons.append(person)
        
        logger.info(f"Found {len(persons)} persons in database")
        return tuple(persons)

    @override
    def add(self, person: PersonUpdateDTO) -> int:
        if not person.label or not person.label.strip():
            raise DTOValueError("Person label cannot be empty")
        
        query = QSqlQuery()
        sql = "INSERT INTO persons (label, description) VALUES (:label, :description)"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.bindValue(":label", person.label.strip())
        query.bindValue(":description", person.description if person.description else "")
        
        if not query.exec():
            error_text = query.lastError().text()
            logger.error(f"Failed to add person: {error_text}")
            raise Exception(f"Database error: {error_text}")
        
        person_id = query.lastInsertId()
        logger.info(f"Added person: {person.label} with ID: {person_id}")
        return person_id

    @override
    def add_with_id(self, person_id: int, label: str, description: str | None = None) -> None:
        """Add person with manual ID."""
        if not label or not label.strip():
            raise DTOValueError("Person label cannot be empty")
        
        query = QSqlQuery()
        sql = "INSERT INTO persons (person_id, label, description) VALUES (:id, :label, :description)"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.bindValue(":id", person_id)
        query.bindValue(":label", label.strip())
        query.bindValue(":description", description if description else "")
        
        if not query.exec():
            error_text = query.lastError().text()
            logger.error(f"Failed to add person with ID {person_id}: {error_text}")
            raise Exception(f"Database error: {error_text}")
        
        logger.info(f"Added person: {label} with manual ID: {person_id}")

    @override
    def update(self, person_id: int, person: PersonUpdateDTO) -> None:
        query = QSqlQuery()
        sql = "UPDATE persons SET label = :label, description = :description WHERE person_id = :id;"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.bindValue(":label", person.label if person.label else "")
        query.bindValue(":description", person.description if person.description else "")
        query.bindValue(":id", person_id)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", person_id)

    @override
    def delete(self, person_id: int) -> bool:
        query = QSqlQuery()
        sql = "DELETE FROM persons WHERE person_id = ?"
        
        if not query.prepare(sql):
            self._raise_on_prepare(query)
        
        query.addBindValue(person_id)
        
        if not query.exec():
            self._raise_on_exec(query)
        
        if query.numRowsAffected() == 0:
            logger.warning("Record with ID %d is not found", person_id)
            return False
        return True

    @staticmethod
    def _build_person(query: QSqlQuery) -> BasePerson | None:
        try:
            person_id = query.value(0)
            label = query.value(1)
            description = query.value(2) if query.value(2) else None
            
            if person_id is None or label is None:
                return None
            
            return Person(int(person_id), str(label), str(description) if description else None)
        except Exception as e:
            logger.error(f"Error building person: {e}")
            return None