from typing import cast

import pytest
from PySide6.QtSql import QSqlQuery

from src.roll.core import IdentifierType, IdentifierUpdateDTO
from src.roll.repositories import IdentifierRepository


class TestIdentifierRepository:
    @pytest.fixture(autouse=True)
    def cleanup_table(self):
        yield
        query = QSqlQuery()
        _ = query.exec("DELETE FROM identifiers")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='identifiers'")

        _ = query.exec("DELETE FROM persons")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='persons'")

    @pytest.fixture(autouse=True)
    def insert_test_user(self):
        _ = QSqlQuery().exec("""
            INSERT INTO persons (label, description)
            VALUES
                ('Test persons 1', 'Test desc 1'),
                ('Test persons 2', 'Test desc 2');
        """)

    @pytest.fixture
    def repository(self, database) -> IdentifierRepository:
        return IdentifierRepository(database)

    # tests
    def test_add_identifier(self, repository: IdentifierRepository):
        person_id = 1
        hash_value = "test_hash"
        identifier_type = IdentifierType.CARD
        new_identifier = IdentifierUpdateDTO(
            person_id=person_id, hash_value=hash_value, identifier_type=identifier_type
        )

        _ = repository.add(new_identifier)

        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE identifier_id = 1;
        """

        _ = query.exec(sql)

        if query.next():
            i_id = cast("int", query.value(0))
            i_hash = cast("str", query.value(1))
            p_id = cast("int", query.value(2))
            i_type = cast("str", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert i_id == 1
        assert i_hash == hash_value
        assert p_id == person_id
        assert i_type == identifier_type.name

    def test_add_multiple_identifier(
        self,
        repository: IdentifierRepository,
    ):
        person_id_1 = person_id_2 = 1
        person_id_3 = 2
        type_1 = type_3 = IdentifierType.CARD
        type_2 = IdentifierType.QR
        hash_value_1 = "test_1"
        hash_value_2 = "test_2"
        hash_value_3 = "test_3"
        new_identifier_1 = IdentifierUpdateDTO(
            person_id=person_id_1, hash_value=hash_value_1, identifier_type=type_1
        )
        new_identifier_2 = IdentifierUpdateDTO(
            person_id=person_id_2, hash_value=hash_value_2, identifier_type=type_2
        )
        new_identifier_3 = IdentifierUpdateDTO(
            person_id=person_id_3, hash_value=hash_value_3, identifier_type=type_3
        )
        i_get_id_1 = repository.add(new_identifier_1)
        i_get_id_2 = repository.add(new_identifier_2)
        i_get_id_3 = repository.add(new_identifier_3)

        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE identifier_id in (1, 2, 3);
        """

        if not query.exec(sql):
            pytest.fail(query.lastError().text())

        if query.next():
            i_id_1 = cast("int", query.value(0))
            i_hash_1 = cast("str", query.value(1))
            p_id_1 = cast("int", query.value(2))
            i_type_1 = cast("str", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            i_id_2 = cast("int", query.value(0))
            i_hash_2 = cast("str", query.value(1))
            p_id_2 = cast("int", query.value(2))
            i_type_2 = cast("str", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            i_id_3 = cast("int", query.value(0))
            i_hash_3 = cast("str", query.value(1))
            p_id_3 = cast("int", query.value(2))
            i_type_3 = cast("str", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert i_id_1 == 1 == i_get_id_1
        assert i_hash_1 == hash_value_1
        assert p_id_1 == person_id_1
        assert i_type_1 == type_1.name

        assert i_id_2 == 2 == i_get_id_2
        assert i_hash_2 == hash_value_2
        assert p_id_2 == person_id_2
        assert i_type_2 == type_2.name

        assert i_id_3 == 3 == i_get_id_3
        assert i_hash_3 == hash_value_3
        assert p_id_3 == person_id_3
        assert i_type_3 == type_3.name

    def test_get_identifier(self, repository: IdentifierRepository):
        person_id = 1
        hash_value = "test"
        identifier_type = IdentifierType.QR
        i_id = repository.add(
            IdentifierUpdateDTO(
                person_id=person_id,
                hash_value=hash_value,
                identifier_type=identifier_type,
            )
        )

        found = repository.get(i_id)

        assert found is not None
        assert found.identifier_id == i_id
        assert found.person_id == person_id
        assert found.hash_value == hash_value
        assert isinstance(found, identifier_type.value)

    def test_get_person_identifiers(self, repository: IdentifierRepository):
        person_id_1 = person_id_2 = 1
        person_id_3 = 2
        type_1 = type_3 = IdentifierType.CARD
        type_2 = IdentifierType.QR
        hash_value_1 = "test_1"
        hash_value_2 = "test_2"
        hash_value_3 = "test_3"
        new_identifier_1 = IdentifierUpdateDTO(
            person_id=person_id_1, hash_value=hash_value_1, identifier_type=type_1
        )
        new_identifier_2 = IdentifierUpdateDTO(
            person_id=person_id_2, hash_value=hash_value_2, identifier_type=type_2
        )
        new_identifier_3 = IdentifierUpdateDTO(
            person_id=person_id_3, hash_value=hash_value_3, identifier_type=type_3
        )

        i_id_1 = repository.add(new_identifier_1)
        i_id_2 = repository.add(new_identifier_2)
        i_id_3 = repository.add(new_identifier_3)

        identifiers_1 = repository.get_by_person(person_id_1)
        identifiers_2 = repository.get_by_person(person_id_3)

        assert len(identifiers_1) == 2
        assert len(identifiers_2) == 1

        found_1 = identifiers_1[0]
        found_2 = identifiers_1[1]
        found_3 = identifiers_2[0]

        assert found_1 is not None
        assert found_1.identifier_id == i_id_1
        assert found_1.person_id == person_id_1
        assert found_1.hash_value == hash_value_1
        assert isinstance(found_1, type_1.value)

        assert found_2 is not None
        assert found_2.identifier_id == i_id_2
        assert found_2.person_id == person_id_2
        assert found_2.hash_value == hash_value_2
        assert isinstance(found_2, type_2.value)

        assert found_3 is not None
        assert found_3.identifier_id == i_id_3
        assert found_3.person_id == person_id_3
        assert found_3.hash_value == hash_value_3
        assert isinstance(found_3, type_3.value)

    def test_get_non_existent_identifier(self, repository: IdentifierRepository):
        assert repository.get(999) is None

    def test_update_identifier(self, repository: IdentifierRepository):
        old_hash = "test_1"
        new_hash = "test_2"
        person_id = 1
        identifier_type = IdentifierType.CARD
        a_id = repository.add(
            IdentifierUpdateDTO(
                person_id=person_id,
                hash_value=old_hash,
                identifier_type=identifier_type,
            )
        )
        update_dto = IdentifierUpdateDTO(hash_value=new_hash)
        repository.update(a_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT identifier_id, hash_value, person_id, identifier_type
        FROM identifiers
        WHERE identifier_id = 1;
        """

        _ = query.exec(sql)

        if query.next():
            i_id = cast("int", query.value(0))
            i_hash = cast("str", query.value(1))
            p_id = cast("int", query.value(2))
            i_type = cast("str", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert i_id == 1
        assert i_hash == new_hash
        assert p_id == person_id
        assert i_type == identifier_type.name

    def test_delete_identifier(self, repository: IdentifierRepository):
        p_id = repository.add(
            IdentifierUpdateDTO(
                person_id=1, hash_value="test", identifier_type=IdentifierType.CARD
            )
        )

        result = repository.delete(p_id)

        assert result
        assert repository.get(p_id) is None

    def test_delete_non_existent_returns_false(self, repository: IdentifierRepository):
        assert not repository.delete(404)
