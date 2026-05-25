from functools import partial

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


class ScannerPanel(QFrame):
    qr_scanned: Signal = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

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

        title = QLabel("🎥 СКАНЕР QR-КОДОВ")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._preview_label: QLabel = QLabel()
        self._preview_label.setObjectName("preview")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setMinimumHeight(400)
        self._preview_label.setText(
            "📷 \n\nЗдесь будет изображение с камеры\n\nВыберите предмет слева,\nзатем начните сканирование"
        )
        layout.addWidget(self._preview_label)

        btn_layout = QHBoxLayout()
        # TODO (asnden): remove scan from photo
        self._image_btn: QPushButton = QPushButton("🖼️ Сканировать с фото")
        _ = self._image_btn.clicked.connect(self._load_image)
        self._video_btn: QPushButton = QPushButton("🎥 Запустить камеру")
        _ = self._video_btn.clicked.connect(self._start_camera)
        self._stop_btn: QPushButton = QPushButton("⏹️ Остановить")
        self._stop_btn.setObjectName("stop")
        self._stop_btn.setEnabled(False)
        _ = self._stop_btn.clicked.connect(self._stop_camera)
        btn_layout.addWidget(self._image_btn)
        btn_layout.addWidget(self._video_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)

        self._status_label: QLabel = QLabel("💡 Выберите предмет слева")
        self._status_label.setStyleSheet(
            "color: #1abc9c; font-size: 12px; padding: 8px; background-color: #2c3e50; border-radius: 6px;"
        )
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

    def _load_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            scaled = pixmap.scaled(
                self._preview_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._preview_label.setPixmap(scaled)
            self._status_label.setText("🖼️ Изображение загружено, распознаю QR...")
            QTimer.singleShot(1000, partial(self._demo_scan))

    def _demo_scan(self) -> None:
        self._status_label.setText("📱 Демо: отсканирован QR-код '12345'")
        self.qr_scanned.emit("12345")

    def _start_camera(self) -> None:
        self._video_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText("🎥 Камера запущена, сканируйте QR-код...")
        self._preview_label.setText(
            "📷 [КАМЕРА]\n\nСканируйте QR-код...\n\n(!!! ВСТАВИТЬ КОД ДЛЯ ЗАХВАТА С КАМЕРЫ !!!)"
        )

    def _stop_camera(self) -> None:
        self._video_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._status_label.setText("⏹️ Камера остановлена")
        self._preview_label.setText("📷 Камера выключена")

    def update_status(self, message: str, is_error: bool = False) -> None:
        color = "#e74c3c" if is_error else "#1abc9c"
        self._status_label.setStyleSheet(
            f"color: {color}; font-size: 12px; padding: 8px; background-color: #2c3e50; border-radius: 6px;"
        )
        self._status_label.setText(message)
