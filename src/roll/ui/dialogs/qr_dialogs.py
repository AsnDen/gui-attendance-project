from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QDialog
from .base import BaseDialog
from roll.view_models.qr_scanner_viewmodel import QRScannerViewModel


class BaseQRDialog(BaseDialog):
    def __init__(self, parent, scanner_vm: QRScannerViewModel):
        super().__init__(parent)
        self._scanner_vm = scanner_vm
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setModal(True)
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)

        self._preview_label = QLabel()
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setFixedHeight(350)
        self._preview_label.setStyleSheet("background-color: black; border-radius: 8px;")
        layout.addWidget(self._preview_label)

        self._status_label = QLabel("Нажмите 'Запустить камеру'")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        btn_layout = QHBoxLayout()
        self._image_btn = QPushButton("Сканировать с фото")
        self._image_btn.clicked.connect(self._load_image)
        self._camera_btn = QPushButton("Запустить камеру")
        self._camera_btn.clicked.connect(self._start_camera)
        self._stop_btn = QPushButton("Остановить")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_camera)
        btn_layout.addWidget(self._image_btn)
        btn_layout.addWidget(self._camera_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)
        self._add_custom_buttons(btn_layout, layout)

    def _add_custom_buttons(self, btn_layout, main_layout):
        pass

    def _connect_signals(self):
        self._scanner_vm.frame_ready.connect(self._on_frame)
        self._scanner_vm.error_occurred.connect(self._on_error)
        self._scanner_vm.scan_started.connect(lambda: self._status_label.setText("Сканирование..."))
        self._scanner_vm.scan_stopped.connect(lambda: self._status_label.setText("Камера остановлена"))

    def _on_frame(self, qimage):
        pixmap = QPixmap.fromImage(qimage)
        scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._preview_label.setPixmap(scaled)

    def _on_error(self, msg):
        self._status_label.setText(f"Ошибка: {msg}")

    def _load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(self._preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._preview_label.setPixmap(scaled)
            self._status_label.setText("Изображение загружено, распознаю QR...")
            QTimer.singleShot(1000, lambda: self._on_qr_demo("demo_hash_1234567890"))

    def _start_camera(self):
        self._scanner_vm.start_scanning()
        self._camera_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)

    def _stop_camera(self):
        self._scanner_vm.stop_scanning()
        self._preview_label.clear()
        self._preview_label.setText("Камера остановлена")
        self._camera_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

    def reject(self):
        self._stop_camera()
        super().reject()

    def _on_qr_demo(self, hash_value):
        raise NotImplementedError


class QRScanDialog(BaseQRDialog):
    def __init__(self, parent, scanner_vm):
        self._scanned_hash = None
        super().__init__(parent, scanner_vm)
        self.setWindowTitle("Сканирование QR-кода")
        self._scanner_vm.qr_detected.connect(self._on_qr)

    def _on_qr(self, hash_value):
        self._scanned_hash = hash_value
        self._stop_camera()
        self.accept()

    def _on_qr_demo(self, hash_value):
        self._on_qr(hash_value)

    def get_hash(self):
        return self._scanned_hash


class QRMarkDialog(BaseQRDialog):
    qr_scanned = Signal(str)

    def __init__(self, parent, scanner_vm, callback):
        self._callback = callback
        super().__init__(parent, scanner_vm)
        self.setWindowTitle("Отметка по QR-коду")
        self._scanner_vm.qr_detected.connect(self._on_qr)

    def _add_custom_buttons(self, btn_layout, main_layout):
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

    def _on_qr(self, hash_value):
        self._callback(hash_value)
        self._status_label.setText("Отмечено! Сканируйте следующий QR или нажмите 'Закрыть'.")

    def _on_qr_demo(self, hash_value):
        self._on_qr(hash_value)