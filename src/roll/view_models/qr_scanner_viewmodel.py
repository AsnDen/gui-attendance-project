import hashlib
import logging

import cv2
from PySide6.QtCore import (
    QObject,
    QThread,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtGui import QImage

from roll.services.qr_reader_service import (
    CameraUnavailableError,
    QRIdentifierReaderService,
)
from roll.services.camera_service import CameraService
from roll.services.exceptions import QRReaderError

logger = logging.getLogger(__name__)


class QRScannerWorker(QObject):
    """Worker that periodically scans camera frames."""

    qr_detected = Signal(str)
    error_occurred = Signal(str)
    camera_status_changed = Signal(bool)
    finished = Signal()
    stop_requested = Signal()
    frame_ready = Signal(object)

    def __init__(self, scanner: QRIdentifierReaderService, scan_interval_ms: int = 100):
        super().__init__()
        self._scanner = scanner
        self._last_qr: str | None = None
        self._scan_interval_ms = scan_interval_ms
        self._timer = None  # будет создан в start() после перемещения в нужный поток
        self.stop_requested.connect(self.stop)

    @Slot()
    def start(self) -> None:
        """Создаём таймер уже в том потоке, где работает worker."""
        logger.info("Starting QR scanner worker")
        self._timer = QTimer()
        self._timer.setInterval(self._scan_interval_ms)
        self._timer.timeout.connect(self._scan)
        self._timer.start()

    @Slot()
    def stop(self) -> None:
        logger.info("Stopping QR scanner worker")
        if self._timer:
            self._timer.stop()
            self._timer = None
        self.finished.emit()

    @Slot()
    def _scan(self) -> None:
        try:
            success, frame = self._scanner.capture_frame()
            if not success:
                return

            # Отправляем кадр для отображения
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(qt_image)

            # Распознаём QR
            decoded_text, _, _ = self._scanner._detector.detectAndDecode(frame)
            if decoded_text:
                normalized = decoded_text.strip()
                qr_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                if qr_hash != self._last_qr:
                    self._last_qr = qr_hash
                    logger.info("QR detected: %s", qr_hash[:16])
                    self.qr_detected.emit(qr_hash)

            self.camera_status_changed.emit(True)

        except CameraUnavailableError as e:
            logger.warning("Camera unavailable: %s", e)
            self.camera_status_changed.emit(False)
            self.error_occurred.emit(str(e))
            self.stop_requested.emit()

        except QRReaderError as e:
            logger.exception("QR scanner error")
            self.error_occurred.emit(str(e))
            self.stop_requested.emit()


class QRScannerViewModel(QObject):
    """ViewModel for QR scanning."""

    qr_detected = Signal(str)
    scan_started = Signal()
    scan_stopped = Signal()
    error_occurred = Signal(str)
    camera_status_changed = Signal(bool)
    frame_ready = Signal(object)

    def __init__(self, camera_id: int = 0, scan_interval_ms: int = 100):
        super().__init__()
        self.camera_id = camera_id
        self._scan_interval_ms = scan_interval_ms

        self._thread: QThread | None = None
        self._worker: QRScannerWorker | None = None
        self._is_scanning = False

    @property
    def is_scanning(self) -> bool:
        return self._is_scanning

    def check_camera_availability(self) -> bool:
        return CameraService.is_camera_available(self.camera_id)

    def start_scanning(self) -> None:
        if self._is_scanning:
            logger.warning("Scanning already active")
            return

        if not self.check_camera_availability():
            error_msg = f"Camera {self.camera_id} is not available"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.camera_status_changed.emit(False)
            return

        logger.info("Starting QR scanning")

        self._thread = QThread()
        self._worker = QRScannerWorker(
            scanner=QRIdentifierReaderService(camera_id=self.camera_id),
            scan_interval_ms=self._scan_interval_ms
        )

        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.start)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._worker.qr_detected.connect(self.qr_detected.emit)
        self._worker.error_occurred.connect(self.error_occurred.emit)
        self._worker.camera_status_changed.connect(self.camera_status_changed.emit)
        self._worker.frame_ready.connect(self.frame_ready.emit)

        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()
        self._is_scanning = True
        self.scan_started.emit()

    def stop_scanning(self) -> None:
        if not self._is_scanning:
            return
        logger.info("Stopping QR scanning")
        if self._worker:
            self._worker.stop_requested.emit()

    @Slot()
    def _on_thread_finished(self) -> None:
        logger.info("QR scanning stopped")
        self._thread = None
        self._worker = None
        self._is_scanning = False
        self.scan_stopped.emit()