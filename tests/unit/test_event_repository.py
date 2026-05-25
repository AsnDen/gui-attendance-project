from datetime import UTC, datetime, timedelta
from typing import cast

import pytest
from PySide6.QtSql import QSqlQuery

from src.roll.core import EventUpdateDTO
from src.roll.repositories import EventRepository
from tests.conftest import VALID_EVENT_DATA, VALID_UPDATE_EVENT_DTO_DATA


class TestEventRepository:
    @pytest.fixture(autouse=True)
    def cleanup_table(self):
        yield
        query = QSqlQuery()
        _ = query.exec("DELETE FROM events")
        _ = query.exec("DELETE FROM sqlite_sequence WHERE name='events'")

    @pytest.fixture
    def repository(self, database) -> EventRepository:
        return EventRepository(database)

    # tests
    @pytest.mark.parametrize(("label", "start", "duration", "desc"), VALID_EVENT_DATA)
    def test_add_event(
        self,
        repository: EventRepository,
        label: str,
        start: datetime,
        duration: timedelta,
        desc: str,
    ):
        new_event = EventUpdateDTO(
            label=label, start_time=start, duration=duration, description=desc
        )

        _ = repository.add(new_event)

        query = QSqlQuery()
        sql = """
        SELECT event_id, label, start_time, duration_seconds, description FROM events
        WHERE event_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            e_id = cast("int", query.value(0))
            e_label = cast("str", query.value(1))
            e_start = cast("str", query.value(2))
            e_duration = cast("int", query.value(3))
            e_desc = cast("str", query.value(4))
        else:
            pytest.fail("Unable to read database.")

        assert e_id == 1
        assert e_label == label
        assert datetime.fromisoformat(e_start) == start
        assert timedelta(seconds=e_duration) == duration
        assert e_desc == desc

    def test_add_multiple_events(
        self,
        repository: EventRepository,
    ):
        label_1 = desc_1 = "test_1"
        label_2 = desc_2 = "test_2"
        start_1 = start_2 = datetime(2026, 5, 23, tzinfo=UTC)
        duration_1 = duration_2 = timedelta(hours=2)
        new_event_1 = EventUpdateDTO(
            label=label_1, start_time=start_1, duration=duration_1, description=desc_1
        )
        new_event_2 = EventUpdateDTO(
            label=label_2, start_time=start_2, duration=duration_2, description=desc_2
        )

        e_get_id_1 = repository.add(new_event_1)
        e_get_id_2 = repository.add(new_event_2)

        query = QSqlQuery()
        sql = """
        SELECT event_id, label, start_time, duration_seconds, description FROM events
        WHERE event_id IN (1, 2)
        """

        _ = query.exec(sql)

        if query.next():
            e_id_1 = cast("int", query.value(0))
            e_label_1 = cast("str", query.value(1))
            e_start_1 = cast("str", query.value(2))
            e_duration_1 = cast("int", query.value(3))
            e_desc_1 = cast("str", query.value(4))
        else:
            pytest.fail("Unable to read database.")

        if query.next():
            e_id_2 = cast("int", query.value(0))
            e_label_2 = cast("str", query.value(1))
            e_start_2 = cast("str", query.value(2))
            e_duration_2 = cast("int", query.value(3))
            e_desc_2 = cast("str", query.value(4))
        else:
            pytest.fail("Unable to read database.")

        assert e_id_1 == 1 == e_get_id_1
        assert e_label_1 == label_1
        assert datetime.fromisoformat(e_start_1) == start_1
        assert timedelta(seconds=e_duration_1) == duration_1
        assert e_desc_1 == desc_1

        assert e_id_2 == 2 == e_get_id_2
        assert e_label_2 == label_2
        assert datetime.fromisoformat(e_start_2) == start_2
        assert timedelta(seconds=e_duration_2) == duration_2
        assert e_desc_2 == desc_2

    @pytest.mark.parametrize(("label", "start", "duration", "desc"), VALID_EVENT_DATA)
    def test_get_event(
        self,
        repository: EventRepository,
        label: str,
        start: datetime,
        duration: timedelta,
        desc: str,
    ):
        e_id = repository.add(
            EventUpdateDTO(
                label=label, start_time=start, duration=duration, description=desc
            )
        )

        found = repository.get(e_id)

        assert found is not None
        assert found.event_id == e_id
        assert found.label == label
        assert found.start_time == start
        assert found.duration == duration
        assert found.description == desc

    def test_get_all_events(
        self,
        repository: EventRepository,
    ):
        label_1 = desc_1 = "test_1"
        label_2 = desc_2 = "test_2"
        start_1 = start_2 = datetime(2026, 5, 23, tzinfo=UTC)
        duration_1 = duration_2 = timedelta(hours=2)
        new_event_1 = EventUpdateDTO(
            label=label_1, start_time=start_1, duration=duration_1, description=desc_1
        )
        new_event_2 = EventUpdateDTO(
            label=label_2, start_time=start_2, duration=duration_2, description=desc_2
        )

        e_id_1 = repository.add(new_event_1)
        e_id_2 = repository.add(new_event_2)

        events = repository.get_all()

        assert len(events) == 2

        found_1 = events[0]
        found_2 = events[1]

        assert found_1 is not None
        assert found_1.event_id == e_id_1
        assert found_1.label == label_1
        assert found_1.start_time == start_1
        assert found_1.duration == duration_1
        assert found_1.description == desc_1

        assert found_2 is not None
        assert found_2.event_id == e_id_2
        assert found_2.label == label_2
        assert found_2.start_time == start_2
        assert found_2.duration == duration_2
        assert found_2.description == desc_2

    def test_get_non_existent_event(self, repository: EventRepository):
        assert repository.get(999) is None

    @pytest.mark.parametrize(
        ("u_label", "u_start", "u_duration", "u_desc"), VALID_UPDATE_EVENT_DTO_DATA
    )
    def test_update_event(
        self,
        repository: EventRepository,
        u_label: str | None,
        u_start: datetime | None,
        u_duration: timedelta | None,
        u_desc: str | None,
    ):
        label = desc = "Test"
        start = datetime(2026, 5, 23, tzinfo=UTC)
        duration = timedelta(hours=2)

        e_id = repository.add(
            EventUpdateDTO(
                label=label, start_time=start, duration=duration, description=desc
            )
        )
        update_dto = EventUpdateDTO(
            label=u_label, start_time=u_start, duration=u_duration, description=u_desc
        )
        repository.update(e_id, update_dto)

        query = QSqlQuery()
        sql = """
        SELECT event_id, label, start_time, duration_seconds, description FROM events
        WHERE event_id = 1
        """

        _ = query.exec(sql)

        if query.next():
            e_id = cast("int", query.value(0))
            e_label = cast("str", query.value(1))
            e_start = cast("str", query.value(2))
            e_duration = cast("int", query.value(3))
            e_desc = cast("str", query.value(4))
        else:
            pytest.fail("Unable to read database.")

        assert e_id == 1
        assert e_label == u_label or label
        assert datetime.fromisoformat(e_start) == u_start or start
        assert timedelta(seconds=e_duration) == u_duration or duration
        assert e_desc == u_desc or desc

    def test_delete_event(self, repository: EventRepository):
        label = desc = "Test"
        start = datetime(2026, 5, 23, tzinfo=UTC)
        duration = timedelta(hours=2)

        e_id = repository.add(
            EventUpdateDTO(
                label=label, start_time=start, duration=duration, description=desc
            )
        )

        result = repository.delete(e_id)

        assert result
        assert repository.get(e_id) is None

    def test_delete_non_existent_returns_false(self, repository: EventRepository):
        assert not repository.delete(404)
