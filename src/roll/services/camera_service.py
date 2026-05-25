import logging
import cv2
from typing import override

from roll.core.interfaces.services import ICameraAvailabilityService

logger = logging.getLogger(__name__)


class CameraService(ICameraAvailabilityService):
    """Service for checking camera availability using OpenCV."""

    @staticmethod
    @override
    def is_camera_available(camera_id: int) -> bool:
        """ """
        logger.info("Checking camera %s availability", camera_id)

        cap = cv2.VideoCapture(camera_id)
        try:
            if not cap.isOpened():
                logger.warning("Camera %s is unavailable", camera_id)
                return False

            success, _ = cap.read()
            if not success:
                logger.warning("Camera %s opened but cannot capture frames", camera_id)
                return False

            logger.info("Camera %s is available", camera_id)
            return True
        except Exception as e:
            logger.error("Unexpected error while checking camera %s: %s", camera_id, e)
            return False
        finally:
            cap.release()

    @staticmethod
    @override
    def get_available_cameras() -> list[int]:
        """Get list of available camera IDs (0..9)."""
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
            except Exception as e:
                logger.debug("Camera %d error: %s", camera_id, e)
            finally:
                cap.release()

        logger.info("Found %d available cameras: %s", len(available), available)
        return available