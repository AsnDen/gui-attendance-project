from PySide6.QtCore import QObject, Signal
from datetime import time, timedelta


class SubjectsManagementViewModel(QObject):
    subjects_changed = Signal()
    show_warning = Signal(str)

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
            old_template = self._template_service.get_template(template_id)
            old_label = old_template.label

            self._template_service.update_template(template_id, label=label, description=description)

            all_events = self._event_service.get_all_events()
            for ev in all_events:
                if ev.label == old_label:
                    self._event_service.update_event(ev.event_id, label=label)

            self.subjects_changed.emit()
            return True
        except Exception as e:
            self.show_warning.emit(str(e))
            return False

    def delete_template(self, template_id: int, label: str):
        try:
            all_events = self._event_service.get_all_events()
            for ev in all_events:
                if ev.label == label:
                    self._event_service.delete_event(ev.event_id)
            self._template_service.delete_template(template_id)
            self.subjects_changed.emit()
            return True
        except Exception as e:
            self.show_warning.emit(str(e))
            return False
