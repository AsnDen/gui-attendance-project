from unittest.mock import MagicMock

import pytest

from src.roll.core import BasePerson, IPersonRepository, PersonUpdateDTO
from src.roll.services import EmptyLabelError, PersonNotFoundError, PersonService
from tests.conftest import INVALID_PERSON_DATA, VALID_PERSON_DATA


class TestPersonService:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        return MagicMock(spec=IPersonRepository)

    @pytest.fixture
    def service(self, mock_repo: MagicMock) -> PersonService:
        return PersonService(repo=mock_repo)

    @pytest.mark.parametrize(("label", "description"), VALID_PERSON_DATA)
    def test_add_person_success(
        self,
        service: PersonService,
        mock_repo: MagicMock,
        label: str,
        description: str,
    ):
        mock_repo.add.return_value = 42

        result = service.add_person(label, description)

        assert result == 42
        mock_repo.add.assert_called_once_with(
            PersonUpdateDTO(label=label, description=description)
        )

    @pytest.mark.parametrize(("label", "description"), INVALID_PERSON_DATA)
    def test_add_person_raises_empty_label_error(
        self,
        service: PersonService,
        mock_repo: MagicMock,
        label: str,
        description: str,
    ):
        with pytest.raises(EmptyLabelError):
            _ = service.add_person(label=label, description=description)

        mock_repo.add.assert_not_called()

    def test_get_person_success(self, service: PersonService, mock_repo: MagicMock):
        expected_person = MagicMock(spec=BasePerson)
        mock_repo.get.return_value = expected_person

        result = service.get_person(1)

        assert result is expected_person
        mock_repo.get.assert_called_once_with(1)

    def test_get_person_raises_person_not_found_error(
        self, service: PersonService, mock_repo: MagicMock
    ):
        mock_repo.get.return_value = None

        with pytest.raises(PersonNotFoundError):
            _ = service.get_person(999)

        mock_repo.get.assert_called_once_with(999)

    def test_get_all_persons(self, service: PersonService, mock_repo: MagicMock):
        expected_tuple = (MagicMock(spec=BasePerson), MagicMock(spec=BasePerson))
        mock_repo.get_all.return_value = expected_tuple

        result = service.get_all_persons()

        assert result == expected_tuple
        mock_repo.get_all.assert_called_once()

    @pytest.mark.parametrize(("label", "description"), VALID_PERSON_DATA)
    def test_update_person_success(
        self,
        service: PersonService,
        mock_repo: MagicMock,
        label: str,
        description: str,
    ):
        person_id = 1

        service.update_person(person_id, label=label, description=description)

        mock_repo.update.assert_called_once_with(
            person_id, PersonUpdateDTO(label=label, description=description)
        )

    def test_update_person_raises_empty_label_error(
        self, service: PersonService, mock_repo: MagicMock
    ):
        with pytest.raises(EmptyLabelError):
            service.update_person(1, label="")

        mock_repo.update.assert_not_called()

    def test_delete_person_success(self, service: PersonService, mock_repo: MagicMock):
        mock_repo.delete.return_value = True

        service.delete_person(1)

        mock_repo.delete.assert_called_once_with(1)

    def test_delete_person_raises_person_not_found_error(
        self, service: PersonService, mock_repo: MagicMock
    ):
        mock_repo.delete.return_value = False

        with pytest.raises(PersonNotFoundError):
            service.delete_person(999)

        mock_repo.delete.assert_called_once_with(999)
