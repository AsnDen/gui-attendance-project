from typing import cast

import pytest
from PySide6.QtSql import QSqlQuery

from src.roll.core import AttendanceStatus, AttendanceUpdateDTO
from src.roll.repositories import AttendanceRepository

# TODO (asnden): test so there is no double recorded attendances.
# so there is no two attendances that have equal person id and event id.


class TestAttendanceRepository:
    @pytest.fixture(autouse=True)
    def cleanup_table(self):
        yield
        query = QSqlQuery()
        _ = query.exec("DELETE FROM attendance")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='attendance'")

        _ = query.exec("DELETE FROM persons")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='persons'")

        _ = query.exec("DELETE FROM events")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='events'")

    @pytest.fixture(autouse=True)
    def insert_test_user(self):
        _ = QSqlQuery().exec("""
            INSERT INTO persons (label, description)
            VALUES
                ('Test persons 1', 'Test desc 1'),
                ('Test persons 2', 'Test desc 2');
        """)

    @pytest.fixture(autouse=True)
    def insert_test_event(self):
        _ = QSqlQuery().exec("""
            INSERT INTO events (label, description, start_time, duration_seconds)
            VALUES
                ('Test event 1', 'Test desc 1', '2026-24-05T00:00:00+00:00', 3600),
                ('Test event 2', 'Test desc 2', '2026-24-04T00:00:00+00:00', 3000);
        """)

    @pytest.fixture
    def repository(self, database) -> AttendanceRepository:
        return AttendanceRepository(database)

    # tests
    def test_add_attendance(self, repository: AttendanceRepository):
        person_id = event_id = 1
        status = AttendanceStatus.ABSENT
        new_attendance = AttendanceUpdateDTO(
            person_id=person_id, event_id=event_id, status=status
        )

        _ = repository.add(new_attendance)

        query = QSqlQuery()
        sql = """
        SELECT attendance_id, person_id, event_id, status FROM attendance
        WHERE attendance_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            a_id = cast("int", query.value(0))
            p_id = cast("int", query.value(1))
            e_id = cast("int", query.value(2))
            a_status = cast("int", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert a_id == 1
        assert p_id == person_id
        assert e_id == event_id
        assert a_status == status.value

    def test_add_multiple_attendance(
        self,
        repository: AttendanceRepository,
    ):
        person_id_1 = event_id_1 = 1
        person_id_2 = event_id_2 = 2
        person_id_3 = 1
        event_id_3 = 2
        status_1 = status_2 = AttendanceStatus.ABSENT
        status_3 = AttendanceStatus.PRESENT
        new_attendance_1 = AttendanceUpdateDTO(
            person_id=person_id_1, event_id=event_id_1, status=status_1
        )
        new_attendance_2 = AttendanceUpdateDTO(
            person_id=person_id_2, event_id=event_id_2, status=status_2
        )
        new_attendance_3 = AttendanceUpdateDTO(
            person_id=person_id_3, event_id=event_id_3, status=status_3
        )
        a_get_id_1 = repository.add(new_attendance_1)
        a_get_id_2 = repository.add(new_attendance_2)
        a_get_id_3 = repository.add(new_attendance_3)

        query = QSqlQuery()
        sql = """
        SELECT attendance_id, person_id, event_id, status FROM attendance
        WHERE attendance_id IN (1, 2, 3);
        """

        _ = query.exec(sql)

        if query.next():
            a_id_1 = cast("int", query.value(0))
            p_id_1 = cast("int", query.value(1))
            e_id_1 = cast("int", query.value(2))
            a_status_1 = cast("int", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            a_id_2 = cast("int", query.value(0))
            p_id_2 = cast("int", query.value(1))
            e_id_2 = cast("int", query.value(2))
            a_status_2 = cast("int", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            a_id_3 = cast("int", query.value(0))
            p_id_3 = cast("int", query.value(1))
            e_id_3 = cast("int", query.value(2))
            a_status_3 = cast("int", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert a_id_1 == 1 == a_get_id_1
        assert p_id_1 == person_id_1
        assert e_id_1 == event_id_1
        assert a_status_1 == status_1.value

        assert a_id_2 == 2 == a_get_id_2
        assert p_id_2 == person_id_2
        assert e_id_2 == event_id_2
        assert a_status_2 == status_2.value

        assert a_id_3 == 3 == a_get_id_3
        assert p_id_3 == person_id_3
        assert e_id_3 == event_id_3
        assert a_status_3 == status_3.value

    def test_get_attendance(self, repository: AttendanceRepository):
        person_id = 1
        event_id = 1
        status = AttendanceStatus.PRESENT
        a_id = repository.add(
            AttendanceUpdateDTO(person_id=person_id, event_id=event_id, status=status)
        )

        found = repository.get(a_id)

        assert found is not None
        assert found.attendance_id == a_id
        assert found.person_id == person_id
        assert found.event_id == event_id
        assert found.status == status

    def test_get_event_attendances(self, repository: AttendanceRepository):
        person_id_1 = event_id_1 = 1
        person_id_2 = event_id_2 = 2
        person_id_3 = 1
        event_id_3 = 2
        status_1 = status_2 = AttendanceStatus.ABSENT
        status_3 = AttendanceStatus.PRESENT
        new_attendance_1 = AttendanceUpdateDTO(
            person_id=person_id_1, event_id=event_id_1, status=status_1
        )
        new_attendance_2 = AttendanceUpdateDTO(
            person_id=person_id_2, event_id=event_id_2, status=status_2
        )
        new_attendance_3 = AttendanceUpdateDTO(
            person_id=person_id_3, event_id=event_id_3, status=status_3
        )

        a_id_1 = repository.add(new_attendance_1)
        a_id_2 = repository.add(new_attendance_2)
        a_id_3 = repository.add(new_attendance_3)

        attendances_1 = repository.get_by_event(1)
        attendances_2 = repository.get_by_event(2)

        assert len(attendances_1) == 1
        assert len(attendances_2) == 2

        found_1 = attendances_1[0]
        found_2 = attendances_2[0]
        found_3 = attendances_2[1]

        assert found_1 is not None
        assert found_1.attendance_id == a_id_1
        assert found_1.person_id == person_id_1
        assert found_1.event_id == event_id_1
        assert found_1.status == status_1

        assert found_2 is not None
        assert found_2.attendance_id == a_id_2
        assert found_2.person_id == person_id_2
        assert found_2.event_id == event_id_2
        assert found_2.status == status_2

        assert found_3 is not None
        assert found_3.attendance_id == a_id_3
        assert found_3.person_id == person_id_3
        assert found_3.event_id == event_id_3
        assert found_3.status == status_3

    def test_get_non_existent_attendance(self, repository: AttendanceRepository):
        assert repository.get(999) is None

    def test_update_attendance(self, repository: AttendanceRepository):
        old_status = AttendanceStatus.ABSENT
        new_status = AttendanceStatus.PRESENT
        person_id = event_id = 1
        a_id = repository.add(
            AttendanceUpdateDTO(
                person_id=person_id, event_id=event_id, status=old_status
            )
        )
        update_dto = AttendanceUpdateDTO(status=new_status)
        repository.update(a_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT attendance_id, person_id, event_id, status FROM attendance
        WHERE attendance_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            a_id = cast("int", query.value(0))
            p_id = cast("int", query.value(1))
            e_id = cast("int", query.value(2))
            a_status = cast("int", query.value(3))
        else:
            pytest.fail("Unable to read database.")

        assert a_id == 1
        assert p_id == person_id
        assert e_id == event_id
        assert a_status == new_status.value

    def test_delete_attendance(self, repository: AttendanceRepository):
        p_id = repository.add(
            AttendanceUpdateDTO(person_id=1, event_id=1, status=AttendanceStatus.ABSENT)
        )

        result = repository.delete(p_id)

        assert result
        assert repository.get(p_id) is None

    def test_delete_non_existent_returns_false(self, repository: AttendanceRepository):
        assert not repository.delete(404)
