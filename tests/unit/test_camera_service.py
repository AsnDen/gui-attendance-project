import pytest
from unittest.mock import MagicMock, patch

from src.roll.services.camera_service import CameraService
from src.roll.services.exceptions import CameraUnavailableError


class TestCameraService:
    @pytest.fixture
    def service(self):
        return CameraService()

    @patch("src.roll.services.camera_service.cv2.VideoCapture")
    def test_is_camera_available_success(self, mock_vc, service):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, None)
        mock_vc.return_value = mock_cap

        assert CameraService.is_camera_available(0) is True
        mock_cap.release.assert_called_once()

    @patch("src.roll.services.camera_service.cv2.VideoCapture")
    def test_is_camera_available_not_opened(self, mock_vc, service):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_vc.return_value = mock_cap

        assert CameraService.is_camera_available(0) is False
        mock_cap.release.assert_called_once()

    @patch("src.roll.services.camera_service.cv2.VideoCapture")
    def test_is_camera_available_no_frame(self, mock_vc, service):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_vc.return_value = mock_cap

        assert CameraService.is_camera_available(0) is False
        mock_cap.release.assert_called_once()

    @patch("src.roll.services.camera_service.cv2.VideoCapture")
    def test_get_available_cameras(self, mock_vc, service):
        def mock_cam(id):
            cap = MagicMock()
            if id in (0, 2):
                cap.isOpened.return_value = True
                cap.read.return_value = (True, None)
            else:
                cap.isOpened.return_value = False
            return cap

        mock_vc.side_effect = mock_cam

        available = CameraService.get_available_cameras()
        assert available == [0, 2]
        assert mock_vc.call_count == 10