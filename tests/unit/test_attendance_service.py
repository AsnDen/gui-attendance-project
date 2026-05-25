from unittest.mock import MagicMock

import pytest

from src.roll.core import (
    AttendanceStatus,
    AttendanceUpdateDTO,
    BaseAttendance,
    IAttendanceRepository,
    IEventRepository,
    IPersonRepository,
)
from src.roll.services import (
    AttendanceNotFoundError,
    AttendanceService,
    EventNotFoundError,
    PersonNotFoundError,
)


class TestPersonService:
    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        return MagicMock(spec=IAttendanceRepository)

    @pytest.fixture
    def mock_person_repo(self) -> MagicMock:
        return MagicMock(spec=IPersonRepository)

    @pytest.fixture
    def mock_event_repo(self) -> MagicMock:
        return MagicMock(spec=IEventRepository)

    @pytest.fixture
    def service(
        self,
        mock_repo: MagicMock,
        mock_person_repo: MagicMock,
        mock_event_repo: MagicMock,
    ) -> AttendanceService:
        return AttendanceService(
            repo=mock_repo, person_repo=mock_person_repo, event_repo=mock_event_repo
        )

    def test_add_attendance_success(
        self,
        service: AttendanceService,
        mock_repo: MagicMock,
    ):
        mock_repo.add.return_value = 42

        person_id = event_id = 1
        status = AttendanceStatus.ABSENT
        result = service.add_attendance(person_id, event_id, status)

        assert result == 42
        mock_repo.add.assert_called_once_with(
            AttendanceUpdateDTO(person_id=person_id, event_id=event_id, status=status)
        )

    def test_add_attendance_raises_person_not_found_error(
        self,
        service: AttendanceService,
        mock_repo: MagicMock,
        mock_person_repo: MagicMock,
    ):
        mock_person_repo.get.return_value = None
        with pytest.raises(PersonNotFoundError):
            _ = service.add_attendance(2, 1, AttendanceStatus.ABSENT)

        mock_repo.add.assert_not_called()

    def test_add_attendance_raises_event_not_found_error(
        self,
        service: AttendanceService,
        mock_repo: MagicMock,
        mock_event_repo: MagicMock,
    ):
        mock_event_repo.get.return_value = None
        with pytest.raises(EventNotFoundError):
            _ = service.add_attendance(1, 2, AttendanceStatus.ABSENT)

        mock_repo.add.assert_not_called()

    def test_get_attendance_success(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        expected_attendance = MagicMock(spec=BaseAttendance)
        mock_repo.get.return_value = expected_attendance

        result = service.get_attendance(1)

        assert result is expected_attendance
        mock_repo.get.assert_called_once_with(1)

    def test_get_attendance_raises_attendance_not_found_error(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        mock_repo.get.return_value = None

        with pytest.raises(AttendanceNotFoundError):
            _ = service.get_attendance(999)

        mock_repo.get.assert_called_once_with(999)

    def test_get_attendances_by_event(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        expected_tuple = (
            MagicMock(spec=BaseAttendance),
            MagicMock(spec=BaseAttendance),
        )
        mock_repo.get_by_event.return_value = expected_tuple

        result = service.get_event_attendance(20)

        assert result == expected_tuple
        mock_repo.get_by_event.assert_called_once()

    def test_get_attendances_by_event_raises_event_not_found_error(
        self,
        service: AttendanceService,
        mock_repo: MagicMock,
        mock_event_repo: MagicMock,
    ):
        mock_event_repo.get.return_value = None
        with pytest.raises(EventNotFoundError):
            _ = service.get_event_attendance(1)

        mock_repo.get_by_event.assert_not_called()

    def test_update_attendance_success(
        self,
        service: AttendanceService,
        mock_repo: MagicMock,
    ):
        attendance_id = 1

        service.update_attendance(attendance_id, AttendanceStatus.PRESENT)

        mock_repo.update.assert_called_once_with(
            attendance_id, AttendanceUpdateDTO(status=AttendanceStatus.PRESENT)
        )

    def test_update_attendance_raises_attendance_not_found_error(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        attendance_id = 1
        mock_repo.get.return_value = None
        with pytest.raises(AttendanceNotFoundError):
            service.update_attendance(attendance_id, AttendanceStatus.PRESENT)

        mock_repo.update.assert_not_called()

    def test_delete_attendance_success(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        mock_repo.delete.return_value = True

        service.delete_attendance(1)

        mock_repo.delete.assert_called_once_with(1)

    def test_delete_attendance_raises_attendance_not_found_error(
        self, service: AttendanceService, mock_repo: MagicMock
    ):
        mock_repo.delete.return_value = False

        with pytest.raises(AttendanceNotFoundError):
            service.delete_attendance(999)

        mock_repo.delete.assert_called_once_with(999)
