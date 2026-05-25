import logging

from PySide6.QtCore import (
    QObject,
    QThread,
    QTimer,
    Signal,
    Slot,
)

from roll.services.qr_reader_service import (
    CameraUnavailableError,
    QRIdentifierReaderService,
    QRReaderError,
)

from roll.services.camera_service import CameraService

logger = logging.getLogger(__name__)


class QRScannerWorker(QObject):
    """Worker that periodically scans camera frames."""

    qr_detected = Signal(str)
    error_occurred = Signal(str)
    camera_status_changed = Signal(bool)
    finished = Signal()

    def __init__(self, scanner: QRIdentifierReaderService, scan_interval_ms: int = 100):
        """
        Args:
            scanner:
                QR reader service instance.

            scan_interval_ms:
                Delay between frame scans in milliseconds.
        """
        super().__init__()

        self._scanner = scanner
        self._last_qr: str | None = None
        self._timer = QTimer()
        self._timer.setInterval(scan_interval_ms)
        self._timer.timeout.connect(self._scan)

    @Slot()
    def start(self) -> None:
        """Start periodic QR scanning."""
        logger.info("Starting QR scanner worker")
        self._timer.start()

    @Slot()
    def stop(self) -> None:
        """Stop periodic QR scanning."""
        logger.info("Stopping QR scanner worker")
        self._timer.stop()
        self.finished.emit()

    @Slot()
    def _scan(self) -> None:
        """Read and process single camera frame."""
        try:
            result = self._scanner.read_identifier()
            self.camera_status_changed.emit(True)

            if result is not None and result != self._last_qr:
                self._last_qr = result
                logger.info("QR detected: %s", result[:16])
                self.qr_detected.emit(result)

        except CameraUnavailableError as e:
            logger.warning("Camera unavailable: %s", e)
            self.camera_status_changed.emit(False)
            self.error_occurred.emit(str(e))

        except QRReaderError as e:
            logger.exception("QR scanner error")
            self.error_occurred.emit(str(e))


class QRScannerViewModel(QObject):
    """ViewModel for QR scanning."""

    qr_detected = Signal(str)
    scan_started = Signal()
    scan_stopped = Signal()
    error_occurred = Signal(str)
    camera_status_changed = Signal(bool)

    def __init__(self, camera_id: int = 0, scan_interval_ms: int = 100):
        """
        Args:
            camera_id:
                OpenCV camera device identifier.

            scan_interval_ms:
                Delay between frame scans in milliseconds.
        """
        super().__init__()

        self.camera_id = camera_id
        self._scan_interval_ms = scan_interval_ms
        self._camera_service = CameraService(camera_id=camera_id)

        self._thread: QThread | None = None
        self._worker: QRScannerWorker | None = None
        self._is_scanning = False

    @property
    def is_scanning(self) -> bool:
        """Current scanning state."""
        return self._is_scanning

    def check_camera_availability(self) -> bool:
        """Check if camera is available before starting scan."""
        try:
            return self._camera_service.is_camera_available()
        except Exception as e:
            logger.error("Error checking camera: %s", e)
            return False

    def start_scanning(self) -> None:
        """Start QR scanning thread only if camera is available."""
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

        self._thread.finished.connect(self._on_thread_finished)

        self._thread.start()
        self._is_scanning = True
        self.scan_started.emit()

    def stop_scanning(self) -> None:
        """Stop QR scanning thread."""
        if not self._is_scanning:
            return

        logger.info("Stopping QR scanning")

        if self._worker:
            self._worker.stop()

    @Slot()
    def _on_thread_finished(self) -> None:
        """Handle thread shutdown."""
        logger.info("QR scanning stopped")
        self._thread = None
        self._worker = None
        self._is_scanning = False
        self.scan_stopped.emit()
