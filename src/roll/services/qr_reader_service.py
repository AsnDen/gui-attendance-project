import hashlib
import logging
from typing import override

import cv2

from roll.core.interfaces.services import IIdentifierReaderService
from roll.services.exceptions import CameraUnavailableError, FrameCaptureError, QRReaderError

logger = logging.getLogger(__name__)


class QRIdentifierReaderService(IIdentifierReaderService):
    """QR code reader service using OpenCV. Camera is opened once per instance."""

    def __init__(self, camera_id: int = 0):
        """
        Args:
            camera_id: OpenCV camera device identifier (0 = default).
        """
        self.camera_id = camera_id
        self._detector = cv2.QRCodeDetector()
        self._cap = None
        self._open()

    def _open(self) -> None:
        """Open camera connection and keep it open."""
        logger.info("Opening camera %s", self.camera_id)
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            cap.release()
            logger.warning("Camera %s is unavailable", self.camera_id)
            raise CameraUnavailableError(f"Camera {self.camera_id} is unavailable")
        self._cap = cap

    def _close(self) -> None:
        """Release camera resources."""
        if self._cap:
            logger.info("Closing camera %s", self.camera_id)
            self._cap.release()
            self._cap = None

    def __del__(self):
        """Ensure camera is closed on object destruction."""
        self._close()

    @override
    def read_identifier(self) -> str | None:
        """Read single frame from open camera and extract QR hash."""
        if self._cap is None:
            raise CameraUnavailableError(f"Camera {self.camera_id} is not opened")

        try:
            success, frame = self._cap.read()
            if not success:
                raise FrameCaptureError(f"Failed to capture frame from camera {self.camera_id}")

            decoded_text, _, _ = self._detector.detectAndDecode(frame)
            if not decoded_text:
                return None

            normalized = decoded_text.strip()
            logger.info("QR code detected")
            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        except (CameraUnavailableError, FrameCaptureError):
            raise
        except Exception as e:
            logger.exception("Unexpected error during QR reading: %s", e)
            raise QRReaderError(f"QR reading failed: {e}") from e