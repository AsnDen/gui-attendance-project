from PySide6.QtCore import QObject, Signal
from datetime import time, timedelta


class SubjectsManagementViewModel(QObject):
    subjects_changed = Signal()
    show_warning = Signal(str)
    show_success = Signal(str)

    def __init__(self, template_service, event_service):
        super().__init__()
        self._template_service = template_service
        self._event_service = event_service

    def get_all_templates(self):
        return self._template_service.get_all_templates()

    def add_template(self, label: str, description: str):
        if not label.strip():
            self.show_warning.emit("Название предмета не может быть пустым.")
            return False
        try:
            self._template_service.add_template(
                label=label,
                description=description,
                start_time=time(9, 0),
                duration=timedelta(minutes=90)
            )
            self.show_success.emit(f"Предмет '{label}' добавлен.")
            self.subjects_changed.emit()
            return True
        except Exception as e:
            self.show_warning.emit(str(e))
            return False

    def update_template(self, template_id: int, label: str, description: str):
        if not label.strip():
            self.show_warning.emit("Название не может быть пустым.")
            return False
        try:
            self._template_service.update_template(template_id, label=label, description=description)
            self.show_success.emit("Предмет обновлён.")
            self.subjects_changed.emit()
            return True
        except Exception as e:
            self.show_warning.emit(str(e))
            return False

    def delete_template(self, template_id: int, label: str):
        try:
            # Удалить все события с таким же названием
            all_events = self._event_service.get_all_events()
            deleted_count = 0
            for ev in all_events:
                if ev.label == label:
                    self._event_service.delete_event(ev.event_id)
                    deleted_count += 1
            self._template_service.delete_template(template_id)
            self.show_success.emit(f"Предмет '{label}' удалён. Удалено {deleted_count} занятий.")
            self.subjects_changed.emit()
            return True
        except Exception as e:
            self.show_warning.emit(str(e))
            return False