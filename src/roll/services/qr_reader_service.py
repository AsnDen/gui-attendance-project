import logging
from threading import Event
from typing import Optional
from overrides import override

import cv2

from roll.core.interfaces.services import IIdentifierReaderService

logger = logging.getLogger(__name__)


class QRIdentifierReaderService(IIdentifierReaderService):
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id

    @override
    def read_identifier(self) -> str:
        cap = None
        for cam_id in [self.camera_id, 0, 1, 2]:
            cap = cv2.VideoCapture(cam_id)
            if cap.isOpened():
                logger.info(f"Camera {cam_id} opened")
                break
            if cap:
                cap.release()
                cap = None

        if cap is None or not cap.isOpened():
            logger.error("No camera available")
            return ""

        qr_detector = cv2.QRCodeDetector()
        result_event = Event()
        result = [""]

        def on_qr_scanned(qr_text: str):
            result[0] = qr_text
            result_event.set()

        import threading
        stop_scan = threading.Event()

        def scan_loop():
            while not stop_scan.is_set():
                ret, frame = cap.read()
                if not ret:
                    continue
                decoded_text, _, _ = qr_detector.detectAndDecode(frame)
                if decoded_text:
                    on_qr_scanned(decoded_text)
                    break
            cap.release()

        scanner_thread = threading.Thread(target=scan_loop, daemon=True)
        scanner_thread.start()

        if result_event.wait(timeout=30.0):
            stop_scan.set()
            scanner_thread.join(timeout=1)
            return result[0]
        else:
            stop_scan.set()
            scanner_thread.join(timeout=1)
            logger.warning("QR scan timeout")
            return ""
