import logging
from typing import override

from roll.core import BasePerson, IPersonRepository, IPersonService, PersonUpdateDTO
from roll.services.exceptions import EmptyLabelError, PersonNotFoundError

logger = logging.getLogger(__name__)


class PersonService(IPersonService):
    def __init__(self, repo: IPersonRepository) -> None:
        """Initializes person service with person repository."""
        self.repo: IPersonRepository = repo
        logger.info("Initialized person service")

    @override
    def add_person(self, label: str, description: str = "") -> int:
        if label == "":
            raise EmptyLabelError

        person = PersonUpdateDTO(label=label, description=description)
        return self.repo.add(person)

    @override
    def get_person(self, person_id: int) -> BasePerson:
        person = self.repo.get(person_id)

        if person is None:
            raise PersonNotFoundError

        return person

    @override
    def get_all_persons(self) -> tuple[BasePerson, ...]:
        return self.repo.get_all()

    @override
    def update_person(
        self,
        person_id: int,
        *,
        label: str | None = None,
        description: str | None = None,
    ) -> None:
        if label == "":
            raise EmptyLabelError

        person = PersonUpdateDTO(label=label, description=description)
        self.repo.update(person_id, person)

    @override
    def delete_person(self, person_id: int) -> None:
        if not self.repo.delete(person_id):
            raise PersonNotFoundError
