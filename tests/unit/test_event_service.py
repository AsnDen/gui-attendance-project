from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.roll.core import BaseEvent, EventUpdateDTO, IEventRepository
from src.roll.services import (
    EmptyLabelError,
    EventNotFoundError,
    EventService,
    ZeroDurationError,
)
from tests.conftest import (
    INVALID_EVENT_DATA,
    VALID_EVENT_DATA,
    VALID_UPDATE_EVENT_DTO_DATA,
)


class TestEventService:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        return MagicMock(spec=IEventRepository)

    @pytest.fixture
    def service(self, mock_repo: MagicMock) -> EventService:
        return EventService(repo=mock_repo)

    @pytest.mark.parametrize(
        ("label", "start_time", "duration", "description"), VALID_EVENT_DATA
    )
    def test_add_event_success(
        self,
        service: EventService,
        mock_repo: MagicMock,
        label: str,
        start_time: datetime,
        duration: timedelta,
        description: str,
    ):
        mock_repo.add.return_value = 42

        result = service.add_event(label, start_time, duration, description)

        assert result == 42
        mock_repo.add.assert_called_once_with(
            EventUpdateDTO(
                label=label,
                start_time=start_time,
                duration=duration,
                description=description,
            )
        )

    @pytest.mark.parametrize(
        ("label", "start_time", "duration", "description"), INVALID_EVENT_DATA
    )
    def test_add_event_raises_error_in_invalid_data(
        self,
        service: EventService,
        mock_repo: MagicMock,
        label: str,
        start_time: datetime,
        duration: timedelta,
        description: str,
    ):
        with pytest.raises((EmptyLabelError, ZeroDurationError)):
            _ = service.add_event(
                label=label,
                start_time=start_time,
                duration=duration,
                description=description,
            )

        mock_repo.add.assert_not_called()

    def test_get_event_success(self, service: EventService, mock_repo: MagicMock):
        expected_event = MagicMock(spec=BaseEvent)
        mock_repo.get.return_value = expected_event

        result = service.get_event(1)

        assert result is expected_event
        mock_repo.get.assert_called_once_with(1)

    def test_get_event_raises_event_not_found_error(
        self, service: EventService, mock_repo: MagicMock
    ):
        mock_repo.get.return_value = None

        with pytest.raises(EventNotFoundError):
            _ = service.get_event(999)

        mock_repo.get.assert_called_once_with(999)

    def test_get_all_events(self, service: EventService, mock_repo: MagicMock):
        expected_tuple = (MagicMock(spec=BaseEvent), MagicMock(spec=BaseEvent))
        mock_repo.get_all.return_value = expected_tuple

        result = service.get_all_events()

        assert result == expected_tuple
        mock_repo.get_all.assert_called_once()

    @pytest.mark.parametrize(
        ("label", "start_time", "duration", "description"), VALID_UPDATE_EVENT_DTO_DATA
    )
    def test_update_event_success(
        self,
        service: EventService,
        mock_repo: MagicMock,
        label: str,
        start_time: datetime,
        duration: timedelta,
        description: str,
    ):
        event_id = 1

        service.update_event(
            event_id,
            label=label,
            start_time=start_time,
            duration=duration,
            description=description,
        )

        mock_repo.update.assert_called_once_with(
            event_id,
            EventUpdateDTO(
                label=label,
                start_time=start_time,
                duration=duration,
                description=description,
            ),
        )

    def test_update_event_raises_empty_label_error(
        self, service: EventService, mock_repo: MagicMock
    ):
        with pytest.raises(EmptyLabelError):
            service.update_event(1, label="")

        mock_repo.update.assert_not_called()

    def test_update_event_raises_zero_duration_error(
        self, service: EventService, mock_repo: MagicMock
    ):
        with pytest.raises(ZeroDurationError):
            service.update_event(1, duration=timedelta(seconds=0))

        mock_repo.update.assert_not_called()

    def test_delete_event_success(self, service: EventService, mock_repo: MagicMock):
        mock_repo.delete.return_value = True

        service.delete_event(1)

        mock_repo.delete.assert_called_once_with(1)

    def test_delete_event_raises_event_not_found_error(
        self, service: EventService, mock_repo: MagicMock
    ):
        mock_repo.delete.return_value = False

        with pytest.raises(EventNotFoundError):
            service.delete_event(999)

        mock_repo.delete.assert_called_once_with(999)
