import hashlib
import pytest
from unittest.mock import MagicMock, patch

from src.roll.services.qr_reader_service import (
    QRIdentifierReaderService,
    CameraUnavailableError,
    FrameCaptureError,
)


# -------------------------------------------------
# 1. SUCCESS: QR detected
# -------------------------------------------------
def test_read_identifier_success_with_qr():
    with patch("src.roll.services.qr_reader_service.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "frame")
        mock_vc.return_value = mock_cap

        service = QRIdentifierReaderService(camera_id=0)

        mock_detector = MagicMock()
        mock_detector.detectAndDecode.return_value = ("https://example.com", None, None)
        service._detector = mock_detector

        result = service.read_identifier()

        expected = hashlib.sha256(b"https://example.com").hexdigest()

        assert result == expected


# -------------------------------------------------
# 2. SUCCESS: no QR found
# -------------------------------------------------
def test_read_identifier_no_qr_code():
    with patch("src.roll.services.qr_reader_service.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, "frame")
        mock_vc.return_value = mock_cap

        service = QRIdentifierReaderService(camera_id=0)

        mock_detector = MagicMock()
        mock_detector.detectAndDecode.return_value = ("", None, None)
        service._detector = mock_detector

        result = service.read_identifier()

        assert result is None


# -------------------------------------------------
# 3. ERROR: camera not available (in __init__)
# -------------------------------------------------
def test_camera_not_opened():
    with patch("src.roll.services.qr_reader_service.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_vc.return_value = mock_cap

        with pytest.raises(CameraUnavailableError):
            QRIdentifierReaderService(camera_id=0)


# -------------------------------------------------
# 4. ERROR: frame capture failed
# -------------------------------------------------
def test_frame_capture_failed():
    with patch("src.roll.services.qr_reader_service.cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (False, None)
        mock_vc.return_value = mock_cap

        service = QRIdentifierReaderService(camera_id=0)

        with pytest.raises(FrameCaptureError):
            service.read_identifier()