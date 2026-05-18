import logging
import time
from typing import Optional

import cv2
from overrides import override

from roll.core.interfaces.services import IIdentifierReaderService

logger = logging.getLogger(__name__)


class QRIdentifierReaderService(IIdentifierReaderService):
    SCAN_TIMEOUT_SECONDS = 30
    RETRY_DELAY_SECONDS = 0.05

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id

    @override
    def read_identifier(self) -> str:
        cap = self._open_camera()

        if cap is None:
            logger.error("Unable to open camera")
            return ""

        detector = cv2.QRCodeDetector()

        try:
            deadline = time.monotonic() + self.SCAN_TIMEOUT_SECONDS

            while time.monotonic() < deadline:
                success, frame = cap.read()

                if not success:
                    time.sleep(self.RETRY_DELAY_SECONDS)
                    continue

                decoded_text, _, _ = detector.detectAndDecode(frame)

                if decoded_text:
                    logger.info("QR code detected")
                    return decoded_text.strip()

            logger.warning("QR scan timed out")
            return ""

        except Exception:
            logger.exception("Unexpected error during QR scan")
            return ""

        finally:
            cap.release()

    def _open_camera(self) -> Optional[cv2.VideoCapture]:
        checked_ids = []

        for cam_id in [self.camera_id, 0, 1, 2]:
            if cam_id in checked_ids:
                continue

            checked_ids.append(cam_id)

            cap = cv2.VideoCapture(cam_id)

            if cap.isOpened():
                logger.info("Camera %s opened", cam_id)
                return cap

            logger.debug("Camera %s unavailable", cam_id)
            cap.release()

        return None
