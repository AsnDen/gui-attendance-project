import logging
from typing import override

from roll.core import (
    BaseIdentifier,
    BasePerson,
    IIdentifierRepository,
    IIdentifierService,
    IPersonRepository,
    IdentifierType,
    IdentifierUpdateDTO,
)
from roll.services.exceptions import IdentifierNotFoundError, PersonNotFoundError

logger = logging.getLogger(__name__)


class IdentifierService(IIdentifierService):
    def __init__(self, repo: IIdentifierRepository, person_repo: IPersonRepository) -> None:
        self.repo = repo
        self.person_repo = person_repo
        logger.info("Initialized identifier service")

    @override
    def get_identifier(self, identifier_id: int) -> BaseIdentifier:
        ident = self.repo.get(identifier_id)
        if ident is None:
            raise IdentifierNotFoundError
        return ident

    @override
    def get_person_identifiers(self, person_id: int) -> tuple[BaseIdentifier, ...]:
        if not self.person_repo.get(person_id):
            raise PersonNotFoundError
        return self.repo.get_by_person(person_id)

    @override
    def add_identifier(self, hash_value: str, person_id: int) -> int:
        if not self.person_repo.get(person_id):
            raise PersonNotFoundError
        dto = IdentifierUpdateDTO(
            person_id=person_id,
            hash_value=hash_value,
            identifier_type=IdentifierType.QR,
        )
        return self.repo.add(dto)

    @override
    def update_identifier(self, identifier_id: int, hash_value: str) -> None:
        if not self.repo.get(identifier_id):
            raise IdentifierNotFoundError
        dto = IdentifierUpdateDTO(hash_value=hash_value)
        self.repo.update(identifier_id, dto)

    @override
    def delete_identifier(self, identifier_id: int) -> None:
        if not self.repo.delete(identifier_id):
            raise IdentifierNotFoundError

    @override
    def find_person_by_hash(self, hash_value: str) -> BasePerson | None:
        """Ищет человека по хэшу идентификатора (QR или карты)."""
        for person in self.person_repo.get_all():
            identifiers = self.repo.get_by_person(person.person_id)
            for ident in identifiers:
                if ident.hash_value == hash_value:
                    return person
        return None