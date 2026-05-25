import logging
import cv2
from typing import override

from roll.core.interfaces.services import ICameraAvailabilityService

logger = logging.getLogger(__name__)


class CameraUnavailableError(Exception):
    """Raised when camera cannot be opened."""


class CameraService(ICameraAvailabilityService):
    """Service for checking camera availability."""

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id

    @override
    def is_camera_available(self) -> bool:
        """Check if camera is available without keeping it open."""
        logger.info("Checking camera %s availability", self.camera_id)

        cap = cv2.VideoCapture(self.camera_id)

        try:
            if not cap.isOpened():
                logger.warning("Camera %s is unavailable", self.camera_id)
                return False

            success, _ = cap.read()

            if not success:
                logger.warning("Camera %s opened but cannot capture frames", self.camera_id)
                return False

            logger.info("Camera %s is available", self.camera_id)
            return True

        finally:
            cap.release()

    @override
    def get_available_cameras(self) -> list[int]:
        """Get list of available camera IDs."""
        available = []

        for camera_id in range(10):
            cap = cv2.VideoCapture(camera_id)

            try:
                if cap.isOpened():
                    success, _ = cap.read()
                    if success:
                        available.append(camera_id)
                        logger.debug("Camera %d is available", camera_id)
                    else:
                        logger.debug("Camera %d opened but no frames", camera_id)
            finally:
                cap.release()

        logger.info("Found %d available cameras: %s", len(available), available)
        return available
