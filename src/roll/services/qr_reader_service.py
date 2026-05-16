import logging
from threading import Thread, Event
from typing import Callable, Optional
from overrides import override

import cv2

from roll.core.interfaces import IIdentifierReaderService

logger = logging.getLogger(__name__)


class QRScanner:
    
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._callback: Optional[Callable[[str], None]] = None
        self._is_scanning = False
    
    def start(self, callback: Callable[[str], None]) -> None:
        if self._is_scanning:
            logger.warning("Scanner already running")
            return
        
        self._callback = callback
        self._stop_event.clear()
        self._is_scanning = True
        self._thread = Thread(target=self._scan_loop, daemon=True)
        self._thread.start()
        logger.info("QR scanner started")
    
    def stop(self) -> None:
        self._is_scanning = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("QR scanner stopped")
    
    def _scan_loop(self) -> None:
        cap = None
        # Try different camera indices
        for cam_id in [self.camera_id, 0, 1, 2]:
            cap = cv2.VideoCapture(cam_id)
            if cap.isOpened():
                logger.info(f"Camera {cam_id} opened successfully")
                break
            else:
                cap.release()
                cap = None
        
        if cap is None or not cap.isOpened():
            logger.error("No camera available")
            self._is_scanning = False
            if self._callback:
                self._callback("")
            return
        
        qr_detector = cv2.QRCodeDetector()
        
        while self._is_scanning and not self._stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                continue
            
            decoded_text, points, _ = qr_detector.detectAndDecode(frame)
            
            if decoded_text:
                logger.info(f"QR code read: {decoded_text}")
                cap.release()
                
                if self._callback:
                    self._callback(decoded_text)
                
                return
        
        cap.release()


class QRIdentifierReaderService(IIdentifierReaderService):
    def __init__(self, camera_id: int = 0):
        self._scanner = QRScanner(camera_id)
        self._last_result: Optional[str] = None
    
    @override
    def read_identifier(self) -> str:
        self._last_result = None
        result_event = Event()
        
        def on_qr_scanned(qr_text: str):
            self._last_result = qr_text
            result_event.set()
        
        self._scanner.start(on_qr_scanned)
        
        if result_event.wait(timeout=30.0):
            self._scanner.stop()
            return self._last_result if self._last_result else ""
        else:
            self._scanner.stop()
            logger.warning("QR scan timeout")
            return ""
    
    def start_scanning(self, callback: Callable[[str], None]) -> None:
        self._scanner.start(callback)
    
    def stop_scanning(self) -> None:
        self._scanner.stop()
