import logging
from threading import Event, Thread
from typing import Callable

from roll.services.qr_reader_service import (
    QRIdentifierReaderService,
    QRReaderError,
    CameraUnavailableError,
)

logger = logging.getLogger(__name__)


class QRScannerViewModel:
    def __init__(
        self,
        camera_id: int = 0,
        scan_interval: float = 0.1,
    ):
        self.camera_id = camera_id
        self.scan_interval = scan_interval

        self._scanner = QRIdentifierReaderService(camera_id)

        self._scan_thread: Thread | None = None
        self._stop_event = Event()

        self._is_scanning = False

        self._last_qr: str | None = None

        self.on_qr_detected: Callable[[str], None] | None = None
        self.on_scan_started: Callable[[], None] | None = None
        self.on_scan_stopped: Callable[[], None] | None = None
        self.on_error: Callable[[str], None] | None = None
        self.on_camera_status_changed: Callable[[bool], None] | None = None

    @property
    def is_scanning(self) -> bool:
        return self._is_scanning

    def start_scanning(self) -> None:
        """Start background QR scanning."""

        if self._is_scanning:
            logger.warning("Scanning already active")
            return

        try:
            self._scanner.open()

            self._notify_camera_status(True)

        except CameraUnavailableError as e:
            logger.error("Failed to open camera: %s", e)

            self._notify_camera_status(False)
            self._notify_error(str(e))

            return

        self._stop_event.clear()

        self._is_scanning = True

        self._scan_thread = Thread(
            target=self._scan_loop,
            daemon=True,
            name="qr-scanner-thread",
        )

        self._scan_thread.start()
        logger.info("QR scanning started")
        self._notify_scan_started()

    def stop_scanning(self) -> None:
        """Stop background scanning."""
        if not self._is_scanning:
            return

        logger.info("Stopping QR scanner")

        self._stop_event.set()

        if (
            self._scan_thread
            and self._scan_thread.is_alive()
            and self._scan_thread != Thread.current_thread()
        ):
            self._scan_thread.join(timeout=1.0)

        self._cleanup()

    def _scan_loop(self) -> None:
        """Background scanning loop."""
        try:
            while not self._stop_event.is_set():

                result = self._scanner.read_identifier()

                if result and result != self._last_qr:
                    self._last_qr = result

                    logger.info(
                        "QR detected:",
                        result[:16],
                    )

                    self._notify_qr_detected(result)

                self._stop_event.wait(self.scan_interval)

        except QRReaderError as e:
            logger.exception("QR scanner error")

            self._notify_error(str(e))
            self._notify_camera_status(False)

        except Exception:
            logger.exception("Unexpected scanner error")
            self._notify_error(
                "Unexpected scanner error occurred"
            )
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        self._scanner.close()
        self._is_scanning = False
        self._notify_scan_stopped()

        logger.info("QR scanning stopped")


    def _notify_qr_detected(self, qr_hash: str) -> None:
        if self.on_qr_detected:
            self.on_qr_detected(qr_hash)

    def _notify_scan_started(self) -> None:
        if self.on_scan_started:
            self.on_scan_started()

    def _notify_scan_stopped(self) -> None:
        if self.on_scan_stopped:
            self.on_scan_stopped()

    def _notify_error(self, message: str) -> None:
        if self.on_error:
            self.on_error(message)

    def _notify_camera_status(self, connected: bool) -> None:
        if self.on_camera_status_changed:
            self.on_camera_status_changed(connected)