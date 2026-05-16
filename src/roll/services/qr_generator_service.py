import logging
import qrcode
from pathlib import Path
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QStandardPaths
from io import BytesIO

logger = logging.getLogger(__name__)


class QRGeneratorService:
    def __init__(self):
        app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        self.qr_storage_path = Path(app_data) / "qr_codes"
        self.qr_storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"QR codes stored in: {self.qr_storage_path}")
    
    def generate_qr_for_person(self, person_id: int, label: str) -> bytes:
        qr_data = f"ROLL:{person_id}:{label}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        img_bytes = BytesIO()
        qr_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        qr_file_path = self.qr_storage_path / f"person_{person_id}.png"
        qr_image.save(qr_file_path)
        logger.info(f"QR code saved: {qr_file_path}")
        
        return img_bytes.getvalue()
    
    def get_qr_pixmap(self, person_id: int) -> QPixmap | None:
        qr_file_path = self.qr_storage_path / f"person_{person_id}.png"
        if qr_file_path.exists():
            return QPixmap(str(qr_file_path))
        return None
    
    def delete_qr_for_person(self, person_id: int) -> None:
        qr_file_path = self.qr_storage_path / f"person_{person_id}.png"
        if qr_file_path.exists():
            qr_file_path.unlink()
            logger.info(f"Deleted QR for person {person_id}")