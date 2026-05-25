import hashlib
import logging
from typing import override

import cv2

from roll.core.interfaces.services import IIdentifierReaderService

logger = logging.getLogger(__name__)


class QRReaderError(Exception):
    """Base QR reader exception."""


class CameraUnavailableError(QRReaderError):
    """Raised when camera cannot be opened."""


class FrameCaptureError(QRReaderError):
    """Raised when frame capture fails."""


class QRIdentifierReaderService(IIdentifierReaderService):
    """QR code reader service using OpenCV."""

    def __init__(self, camera_id: int = 0):
        """
        Args:
            camera_id:
                OpenCV camera device identifier.

                Usually:
                - 0 -> default camera
                - 1 -> secondary camera
                - 2+ -> external cameras

                Available ids depend on OS and hardware.
        """
        self.camera_id = camera_id
        self._detector = cv2.QRCodeDetector()

    def _open(self) -> cv2.VideoCapture:
        """Open camera connection.

        Raises:
            CameraUnavailableError:
                If camera cannot be opened.
        """
        logger.info("Opening camera %s", self.camera_id)

        cap = cv2.VideoCapture(self.camera_id)

        if not cap.isOpened():
            cap.release()
            logger.warning("Camera %s is unavailable", self.camera_id)
            raise CameraUnavailableError(f"Camera {self.camera_id} is unavailable")

        return cap

    def _close(self, cap: cv2.VideoCapture) -> None:
        """Release camera resources."""
        logger.info("Closing camera %s", self.camera_id)
        cap.release()

    @override
    def read_identifier(self) -> str | None:
        """Read single frame and extract QR hash."""
        cap = self._open()

        try:
            success, frame = cap.read()

            if not success:
                raise FrameCaptureError(f"Failed to capture frame from camera {self.camera_id}")

            decoded_text, _, _ = self._detector.detectAndDecode(frame)

            if not decoded_text:
                return None

            normalized = decoded_text.strip()
            logger.info("QR code detected")

            return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

        finally:
            self._close(cap)
