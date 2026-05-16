import logging
from typing import override

from roll.core import BasePerson, IPersonRepository, IPersonService, PersonUpdateDTO
from roll.services.exceptions import EmptyLabelError, PersonNotFoundError

logger = logging.getLogger(__name__)


class PersonService(IPersonService):
    def __init__(self, repo: IPersonRepository) -> None:
        self.repo: IPersonRepository = repo
        logger.info("Initialized person service")

    @override
    def add_person(self, label: str, description: str | None = None) -> int:
        if not label or not label.strip():
            raise EmptyLabelError("Person label cannot be empty")
        
        person = PersonUpdateDTO(label=label.strip(), description=description)
        person_id = self.repo.add(person)
        logger.info(f"Added person: {label} with ID: {person_id}")
        return person_id

    @override
    def add_person_with_id(self, person_id: int, label: str, description: str | None = None) -> None:
        """Add new person with manual ID."""
        if not label or not label.strip():
            raise EmptyLabelError("Person label cannot be empty")
        
        self.repo.add_with_id(person_id, label.strip(), description)
        logger.info(f"Added person: {label} with manual ID: {person_id}")

    @override
    def get_person(self, person_id: int) -> BasePerson:
        person = self.repo.get(person_id)
        if person is None:
            raise PersonNotFoundError(f"Person with ID {person_id} not found")
        return person

    @override
    def get_all_persons(self) -> tuple[BasePerson, ...]:
        return self.repo.get_all()

    @override
    def update_person(self, person_id: int, person: PersonUpdateDTO) -> None:
        if person.label and not person.label.strip():
            raise EmptyLabelError("Person label cannot be empty")
        self.repo.update(person_id, person)

    @override
    def delete_person(self, person_id: int) -> None:
        if not self.repo.delete(person_id):
            raise PersonNotFoundError(f"Person with ID {person_id} not found")