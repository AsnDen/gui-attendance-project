
import logging
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QImage
import cv2
import numpy as np

from roll.services.qr_reader_service import QRIdentifierReaderService
from roll.ui.styles import SCANNER_DIALOG_STYLE

logger = logging.getLogger(__name__)


class ScannerWorker(QThread):
    """Worker thread for QR scanner with video preview."""
    
    qr_scanned = Signal(str)
    frame_ready = Signal(QImage)
    error_occurred = Signal(str)
    
    def __init__(self, camera_id: int = 0):
        super().__init__()
        self.camera_id = camera_id
        self._is_running = False
        self.cap = None
        self.qr_detector = cv2.QRCodeDetector()
        
    def run(self):
        """Run scanner in thread."""
        self._is_running = True
        
        # Try to open camera
        for cam_id in [self.camera_id, 0, 1, 2]:
            self.cap = cv2.VideoCapture(cam_id)
            if self.cap.isOpened():
                logger.info(f"Camera {cam_id} opened successfully")
                break
            else:
                self.cap.release()
                self.cap = None
        
        if self.cap is None or not self.cap.isOpened():
            self.error_occurred.emit("No camera available")
            return
        
        while self._is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            # Convert frame to QImage for display
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(qt_image)
            
            # Try to detect QR code
            decoded_text, points, _ = self.qr_detector.detectAndDecode(frame)
            
            if decoded_text:
                logger.info(f"QR code read: {decoded_text}")
                self.qr_scanned.emit(decoded_text)
                self.stop()
        
        if self.cap:
            self.cap.release()
    
    def stop(self):
        """Stop scanning."""
        self._is_running = False


class QRScannerDialog(QDialog):
    """Dialog for scanning QR codes."""
    
    def __init__(self, parent=None, camera_id: int = 0):
        super().__init__(parent)
        
        self.scanned_data: Optional[str] = None
        self.camera_id = camera_id
        self.scanner_worker: Optional[ScannerWorker] = None
        self.is_scanning = False
        
        self.setWindowTitle("Scan QR Code")
        self.setModal(True)
        self.setMinimumSize(640, 480)
        self.setStyleSheet(SCANNER_DIALOG_STYLE)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        
        # Video preview label
        self.video_label = QLabel()
        self.video_label.setObjectName("video_label")
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("Camera not started")
        self.video_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.video_label)
        
        # Status label
        self.status_label = QLabel("Click 'Start Scanning' to begin")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Scanning")
        self.start_button.setObjectName("scan_button")
        self.start_button.clicked.connect(self._start_scanner)
        self.start_button.setStyleSheet("background-color: #2d6a4f; font-weight: bold;")
        button_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stop_button")
        self.stop_button.clicked.connect(self._stop_scanner)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _start_scanner(self):
        """Start QR scanner."""
        if self.scanner_worker and self.scanner_worker.isRunning():
            logger.warning("Scanner already running")
            return
        
        self.is_scanning = True
        self.status_label.setText("Initializing camera...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.video_label.setText("Starting camera...")
        
        # Create and start scanner worker
        self.scanner_worker = ScannerWorker(self.camera_id)
        self.scanner_worker.qr_scanned.connect(self._on_qr_scanned)
        self.scanner_worker.frame_ready.connect(self._update_frame)
        self.scanner_worker.error_occurred.connect(self._on_error)
        self.scanner_worker.start()
        
        logger.info("Scanner started")
    
    def _update_frame(self, qt_image: QImage):
        """Update video preview."""
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)
        self.status_label.setText("Scanning... Hold QR code in front of camera")
    
    def _stop_scanner(self):
        """Stop QR scanner."""
        if self.scanner_worker:
            self.scanner_worker.stop()
            self.scanner_worker.wait(2000)
            self.scanner_worker = None
        
        self.is_scanning = False
        self.status_label.setText("Scanner stopped")
        self.video_label.setText("Camera stopped")
        self.video_label.setPixmap(QPixmap())
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        logger.info("Scanner stopped")
    
    def _on_qr_scanned(self, qr_string: str):
        """Handle scanned QR code."""
        self.scanned_data = qr_string
        self.status_label.setText(f"QR Code scanned: {qr_string[:30]}...")
        
        # Show success message
        QMessageBox.information(
            self,
            "QR Code Scanned",
            f"Successfully scanned QR code!\n\nData: {qr_string[:50]}...",
            QMessageBox.Ok
        )
        
        self.accept()
    
    def _on_error(self, error_message: str):
        """Handle scanner error."""
        logger.error(f"Scanner error: {error_message}")
        self.status_label.setText(f"Error: {error_message}")
        self.video_label.setText(f"Error: {error_message}")
        QMessageBox.warning(
            self,
            "Scanner Error",
            f"Failed to start scanner:\n{error_message}",
            QMessageBox.Ok
        )
        self._stop_scanner()
    
    def get_scanned_data(self) -> Optional[str]:
        """Get scanned QR code data."""
        return self.scanned_data
    
    def reject(self):
        """Handle dialog rejection."""
        self._stop_scanner()
        super().reject()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        self._stop_scanner()
        event.accept()