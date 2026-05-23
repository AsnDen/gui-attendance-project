from typing import cast

import pytest
from PySide6.QtSql import QSqlQuery

from src.roll.core import PersonUpdateDTO
from src.roll.repositories.person_repository import PersonRepository
from tests.conftest import VALID_PERSON_DATA


class TestPersonRepository:
    @pytest.fixture(autouse=True)
    def cleanup_table(self):
        yield
        query = QSqlQuery()
        _ = query.exec("DELETE FROM persons")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='persons'")

    @pytest.fixture
    def repository(self, database) -> PersonRepository:
        return PersonRepository(database)

    # tests
    @pytest.mark.parametrize(("label", "desc"), VALID_PERSON_DATA)
    def test_add_person(self, repository: PersonRepository, label: str, desc: str):
        new_person = PersonUpdateDTO(label=label, description=desc)

        _ = repository.add(new_person)

        query = QSqlQuery()
        sql = """
        SELECT person_id, label, description FROM persons
        WHERE person_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            p_id = cast("int", query.value(0))
            p_label = cast("str", query.value(1))
            p_desc = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        assert p_id == 1
        assert p_label == label
        assert p_desc == desc

    def test_add_multiple_person(
        self,
        repository: PersonRepository,
    ):
        label_1 = desc_1 = "test_1"
        label_2 = desc_2 = "test_2"
        new_person_1 = PersonUpdateDTO(label=label_1, description=desc_1)
        new_person_2 = PersonUpdateDTO(label=label_2, description=desc_2)

        p_get_id_1 = repository.add(new_person_1)
        p_get_id_2 = repository.add(new_person_2)

        query = QSqlQuery()
        sql = """
        SELECT person_id, label, description FROM persons
        WHERE person_id IN (1, 2)
        """

        _ = query.exec(sql)

        if query.next():
            p_id_1 = cast("int", query.value(0))
            p_label_1 = cast("str", query.value(1))
            p_desc_1 = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            p_id_2 = cast("int", query.value(0))
            p_label_2 = cast("str", query.value(1))
            p_desc_2 = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        assert p_id_1 == 1 == p_get_id_1
        assert p_label_1 == label_1
        assert p_desc_1 == desc_1

        assert p_id_2 == 2 == p_get_id_2
        assert p_label_2 == label_2
        assert p_desc_2 == desc_2

    @pytest.mark.parametrize(("label", "desc"), VALID_PERSON_DATA)
    def test_get_person(self, repository: PersonRepository, label: str, desc: str):
        p_id = repository.add(PersonUpdateDTO(label=label, description=desc))

        found = repository.get(p_id)

        assert found is not None
        assert found.person_id == p_id
        assert found.label == label
        assert found.description == desc

    def test_get_all_persons(
        self,
        repository: PersonRepository,
    ):
        label_1 = desc_1 = "test_1"
        label_2 = desc_2 = "test_2"
        new_person_1 = PersonUpdateDTO(label=label_1, description=desc_1)
        new_person_2 = PersonUpdateDTO(label=label_2, description=desc_2)

        p_id_1 = repository.add(new_person_1)
        p_id_2 = repository.add(new_person_2)

        found_1 = repository.get(p_id_1)
        found_2 = repository.get(p_id_2)

        assert found_1 is not None
        assert found_1.person_id == p_id_1
        assert found_1.label == label_1
        assert found_1.description == desc_1

        assert found_2 is not None
        assert found_2.person_id == p_id_2
        assert found_2.label == label_2
        assert found_2.description == desc_2

    def test_get_non_existent_person(self, repository: PersonRepository):
        assert repository.get(999) is None

    def test_update_person_label(self, repository: PersonRepository):
        label = desc = "Test"
        p_id = repository.add(PersonUpdateDTO(label=label, description=desc))
        updated_label = label + "update"
        update_dto = PersonUpdateDTO(label=updated_label)
        repository.update(p_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT person_id, label, description FROM persons
        WHERE person_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            p_id = cast("int", query.value(0))
            p_label = cast("str", query.value(1))
            p_desc = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        assert p_id == 1
        assert p_label == updated_label
        assert p_desc == desc

    def test_update_person_description(self, repository: PersonRepository):
        label = desc = "Test"
        p_id = repository.add(PersonUpdateDTO(label=label, description=desc))
        updated_label = label + "update"
        updated_desc = desc + "update"
        update_dto = PersonUpdateDTO(label=updated_label, description=updated_desc)
        repository.update(p_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT person_id, label, description FROM persons
        WHERE person_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            p_id = cast("int", query.value(0))
            p_label = cast("str", query.value(1))
            p_desc = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        assert p_id == 1
        assert p_label == updated_label
        assert p_desc == updated_desc

    def test_update_person__label_and_description(self, repository: PersonRepository):
        label = desc = "Test"
        p_id = repository.add(PersonUpdateDTO(label=label, description=desc))
        updated_desc = desc + "update"
        update_dto = PersonUpdateDTO(description=updated_desc)
        repository.update(p_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT person_id, label, description FROM persons
        WHERE person_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            p_id = cast("int", query.value(0))
            p_label = cast("str", query.value(1))
            p_desc = cast("str", query.value(2))
        else:
            pytest.fail("Unable to read database.")

        assert p_id == 1
        assert p_label == label
        assert p_desc == updated_desc

    def test_delete_person(self, repository: PersonRepository):
        label = desc = "Test"
        p_id = repository.add(PersonUpdateDTO(label=label, description=desc))

        result = repository.delete(p_id)

        assert result
        assert repository.get(p_id) is None

    def test_delete_non_existent_returns_false(self, repository: PersonRepository):
        assert not repository.delete(404)
