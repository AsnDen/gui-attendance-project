import pytest
from unittest.mock import patch

from roll.view_models.qr_scanner_viewmodel import QRScannerViewModel


def test_check_camera_availability():
    with patch("roll.view_models.qr_scanner_viewmodel.CameraService") as MockCamera:
        MockCamera.is_camera_available.return_value = True
        vm = QRScannerViewModel(camera_id=0)
        assert vm.check_camera_availability() is True

        MockCamera.is_camera_available.return_value = False
        assert vm.check_camera_availability() is False


def test_start_scanning_success_creates_worker(qtbot):
    with patch("roll.view_models.qr_scanner_viewmodel.CameraService") as MockCamera, \
         patch("roll.view_models.qr_scanner_viewmodel.QRIdentifierReaderService"), \
         patch("roll.view_models.qr_scanner_viewmodel.QThread") as MockThread, \
         patch("roll.view_models.qr_scanner_viewmodel.QRScannerWorker") as MockWorker:

        MockCamera.is_camera_available.return_value = True
        mock_worker = MockWorker.return_value
        mock_thread = MockThread.return_value

        vm = QRScannerViewModel(camera_id=0)
        vm.start_scanning()

        assert vm.is_scanning is True
        MockWorker.assert_called_once()
        mock_worker.moveToThread.assert_called_once_with(mock_thread)
        mock_thread.start.assert_called_once()


def test_start_scanning_camera_unavailable_emits_error(qtbot):
    with patch("roll.view_models.qr_scanner_viewmodel.CameraService") as MockCamera:
        MockCamera.is_camera_available.return_value = False
        vm = QRScannerViewModel(camera_id=0)

        with qtbot.waitSignal(vm.error_occurred, timeout=1000) as blocker:
            vm.start_scanning()

        assert vm.is_scanning is False
        assert "not available" in blocker.args[0]


def test_stop_scanning_stops_worker(qtbot):
    with patch("roll.view_models.qr_scanner_viewmodel.CameraService") as MockCamera, \
         patch("roll.view_models.qr_scanner_viewmodel.QRIdentifierReaderService"), \
         patch("roll.view_models.qr_scanner_viewmodel.QThread"), \
         patch("roll.view_models.qr_scanner_viewmodel.QRScannerWorker") as MockWorker:

        MockCamera.is_camera_available.return_value = True
        mock_worker = MockWorker.return_value

        vm = QRScannerViewModel(camera_id=0)
        vm.start_scanning()
        vm.stop_scanning()

        mock_worker.stop_requested.emit.assert_called_once()