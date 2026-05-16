
"""Identifier service for managing identifiers."""

import logging
from typing import override, Optional, Tuple
from PySide6.QtSql import QSqlQuery

from roll.core import (
    IIdentifierRepository, IIdentifierService,
    BaseIdentifier, IdentifierUpdateDTO, IdentifierType
)
from roll.services.exceptions import IdentifierNotFoundError

logger = logging.getLogger(__name__)


class IdentifierService(IIdentifierService):
    def __init__(self, repo: IIdentifierRepository):
        self.repo = repo
        logger.info("Initialized identifier service")

    @override
    def add_identifier(self, hash_value: str, person_id: int, identifier_type: IdentifierType) -> None:
        """Add new identifier."""
        identifier = IdentifierUpdateDTO(
            hash_value=hash_value,
            person_id=person_id,
            identifier_type=identifier_type
        )
        self.repo.add(identifier)
        logger.info(f"Added identifier for person {person_id}")

    @override
    def get_identifier(self, identifier_id: int) -> BaseIdentifier:
        """Get identifier by ID."""
        identifier = self.repo.get(identifier_id)
        if identifier is None:
            raise IdentifierNotFoundError(f"Identifier with ID {identifier_id} not found")
        return identifier

    @override
    def update_identifier(self, identifier_id: int, identifier: IdentifierUpdateDTO) -> None:
        """Update existing identifier."""
        self.repo.update(identifier_id, identifier)
        logger.info(f"Updated identifier {identifier_id}")

    @override
    def delete_identifier(self, identifier_id: int) -> None:
        """Delete identifier."""
        if not self.repo.delete(identifier_id):
            raise IdentifierNotFoundError(f"Identifier with ID {identifier_id} not found")
        logger.info(f"Deleted identifier {identifier_id}")
    
    def get_identifier_by_hash(self, hash_value: str) -> Optional[BaseIdentifier]:
        """Get identifier by hash value."""
        return self.repo.get_by_hash(hash_value)
    
    def get_identifiers_by_person(self, person_id: int) -> Tuple[BaseIdentifier, ...]:
        """Get all identifiers for a person."""
        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE person_id = ?
        ORDER BY identifier_id
        """
        
        if not query.prepare(sql):
            logger.error(f"Failed to prepare query: {query.lastError().text()}")
            return ()
        
        query.addBindValue(person_id)
        
        if not query.exec():
            logger.error(f"Failed to execute query: {query.lastError().text()}")
            return ()
        
        identifiers = []
        while query.next():
            identifier_id = query.value(0)
            hash_value = query.value(1)
            person_id_val = query.value(2)
            identifier_type_str = query.value(3)
            
            identifier_type = IdentifierType.QR if identifier_type_str == "QR" else IdentifierType.CARD
            
            identifier = identifier_type.value(identifier_id, person_id_val, hash_value)
            identifiers.append(identifier)
        
        return tuple(identifiers)