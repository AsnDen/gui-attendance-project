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
    """
    QR code reader service using OpenCV.
    """

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id

        self._cap: cv2.VideoCapture | None = None
        self._detector = cv2.QRCodeDetector()

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def open(self) -> None:
        """Open camera connection."""

        if self.is_open:
            return

        logger.info("Opening camera %s", self.camera_id)

        self._cap = cv2.VideoCapture(self.camera_id)

        if not self._cap.isOpened():
            self._cap.release()
            self._cap = None

            raise CameraUnavailableError(
                f"Camera {self.camera_id} is unavailable"
            )

    def close(self) -> None:
        """Release camera resources."""

        if self._cap:
            logger.info("Closing camera %s", self.camera_id)
            self._cap.release()
            self._cap = None

    @override
    def read_identifier(self) -> str | None:
        """
        Read single frame and extract QR hash.
        """

        if not self.is_open:
            raise QRReaderError("Camera is not opened")

        success, frame = self._cap.read()

        if not success:
            raise FrameCaptureError(
                f"Failed to capture frame from camera {self.camera_id}"
            )

        decoded_text, _, _ = self._detector.detectAndDecode(frame)

        if not decoded_text:
            return None

        normalized = decoded_text.strip()

        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()