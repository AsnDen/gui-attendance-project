from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFileDialog, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import shutil

from roll.services.qr_generator_service import QRGeneratorService


class PersonQRDialog(QDialog):
    def __init__(self, parent=None, person_id: int = None, person_name: str = None):
        super().__init__(parent)
        self.person_id = person_id
        self.person_name = person_name
        self.qr_generator = QRGeneratorService()
        
        self.setWindowTitle(f"QR Code - {person_name}")
        self.setModal(False)
        self.setFixedSize(400, 500)
        
        self._setup_ui()
        self._load_qr_code()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.name_label = QLabel(f"<h2>{self.person_name}</h2>")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(300, 300)
        self.qr_label.setStyleSheet("border: 1px solid #4a4a4a; background-color: white;")
        layout.addWidget(self.qr_label)
        
        self.info_label = QLabel("Scan this QR code to mark attendance")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save to File")
        self.save_btn.clicked.connect(self._save_qr_to_file)
        button_layout.addWidget(self.save_btn)
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.regenerate_btn = QPushButton("Regenerate QR Code")
        self.regenerate_btn.setStyleSheet("background-color: #9d0208;")
        self.regenerate_btn.clicked.connect(self._regenerate_qr)
        layout.addWidget(self.regenerate_btn)
    
    def _load_qr_code(self):
        pixmap = self.qr_generator.get_qr_pixmap(self.person_id)
        if pixmap:
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
            self.qr_label.setPixmap(scaled_pixmap)
        else:
            self._regenerate_qr()
    
    def _regenerate_qr(self):
        try:
            qr_data = self.qr_generator.generate_qr_for_person(self.person_id, self.person_name)
            pixmap = QPixmap()
            pixmap.loadFromData(qr_data)
            scaled_pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio)
            self.qr_label.setPixmap(scaled_pixmap)
            QMessageBox.information(self, "Success", "QR code regenerated!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")
    
    def _save_qr_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save QR Code", f"{self.person_name}_qr.png", "PNG Images (*.png)"
        )
        if file_path:
            qr_file = self.qr_generator.qr_storage_path / f"person_{self.person_id}.png"
            if qr_file.exists():
                shutil.copy(qr_file, file_path)
                QMessageBox.information(self, "Success", f"Saved to {file_path}")
    
    def _copy_to_clipboard(self):
        pixmap = self.qr_label.pixmap()
        if pixmap:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            QMessageBox.information(self, "Success", "QR code copied!")