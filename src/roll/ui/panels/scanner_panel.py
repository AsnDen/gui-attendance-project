# src/roll/ui/panels/scanner_panel.py
from functools import partial
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout
)
from roll.view_models.qr_scanner_viewmodel import QRScannerViewModel


class ScannerPanel(QFrame):
    qr_scanned = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._scanner_vm = QRScannerViewModel()
        self._setup_ui()
        self._connect_viewmodel()

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            QFrame { background-color: #34495e; border-radius: 12px; margin: 5px; }
            QLabel#title { color: #ecf0f1; font-size: 16px; font-weight: bold; padding: 10px; background-color: #2c3e50; border-radius: 8px; }
            QPushButton { background-color: #1abc9c; border: none; border-radius: 8px; padding: 12px; color: #2c3e50; font-weight: bold; font-size: 14px; }
            QPushButton:hover { background-color: #16a085; color: white; }
            QPushButton#stop { background-color: #e74c3c; color: white; }
            QLabel#preview { background-color: #2c3e50; border-radius: 10px; color: #7f8c8d; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("СКАНЕР QR-КОДОВ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self._preview_label = QLabel()
        self._preview_label.setObjectName("preview")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setFixedHeight(400)
        self._preview_label.setMinimumWidth(500)
        self._preview_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._preview_label.setText("Здесь будет изображение с камеры\n\nВыберите предмет слева,\nзатем начните сканирование")
        layout.addWidget(self._preview_label)

        btn_layout = QHBoxLayout()
        self._image_btn = QPushButton("Сканировать с фото")
        self._image_btn.clicked.connect(self._load_image)
        self._video_btn = QPushButton("Запустить камеру")
        self._video_btn.clicked.connect(self._start_camera)
        self._stop_btn = QPushButton("Остановить")
        self._stop_btn.setObjectName("stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_camera)
        btn_layout.addWidget(self._image_btn)
        btn_layout.addWidget(self._video_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)

        self._status_label = QLabel("Выберите предмет слева")
        self._status_label.setStyleSheet("color: #1abc9c; font-size: 12px; padding: 8px; background-color: #2c3e50; border-radius: 6px;")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

    def _connect_viewmodel(self) -> None:
        self._scanner_vm.qr_detected.connect(self._on_qr_detected)
        self._scanner_vm.error_occurred.connect(lambda msg: self.update_status(msg, True))
        self._scanner_vm.camera_status_changed.connect(self._on_camera_status)
        self._scanner_vm.scan_started.connect(lambda: self.update_status("Сканирование запущено"))
        self._scanner_vm.scan_stopped.connect(lambda: self.update_status("Сканирование остановлено"))
        self._scanner_vm.frame_ready.connect(self._on_frame_ready)

    def _on_frame_ready(self, qimage) -> None:
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview_label.setPixmap(scaled)
        self._preview_label.setAlignment(Qt.AlignCenter)

    def _on_qr_detected(self, hash_value: str) -> None:
        self.qr_scanned.emit(hash_value)

    def _on_camera_status(self, available: bool) -> None:
        if not available:
            self.update_status("Камера недоступна", True)

    def _load_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._preview_label.setPixmap(scaled)
            self._status_label.setText("Изображение загружено, распознаю QR...")
            QTimer.singleShot(1000, partial(self._demo_scan))

    def _demo_scan(self) -> None:
        self._status_label.setText("Демо: отсканирован QR-код '12345'")
        self.qr_scanned.emit("12345")

    def _start_camera(self) -> None:
        self._scanner_vm.start_scanning()
        self._video_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def _stop_camera(self) -> None:
        self._scanner_vm.stop_scanning()
        self._video_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def update_status(self, message: str, is_error: bool = False) -> None:
        color = "#e74c3c" if is_error else "#1abc9c"
        self._status_label.setStyleSheet(f"color: {color}; font-size: 12px; padding: 8px; background-color: #2c3e50; border-radius: 6px;")
        self._status_label.setText(message)