import logging
import sys

from PySide6.QtWidgets import QApplication

from roll.core import init_database, setup_logging
from roll.repositories import (
    AttendanceRepository,
    EventRepository,
    EventTemplateRepository,
    IdentifierRepository,
    PersonRepository,
)
from roll.services import (
    AttendanceService,
    EventService,
    EventTemplateService,
    PersonService,
)
from roll.ui import MainWindow
from roll.view_models import ViewModelFactory


def main() -> None:
    """Program entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("roll")
    app.setOrganizationName("roll")

    setup_logging()
    logger = logging.getLogger("roll")
    logger.info("Starting program")

    db = init_database()

    person_repo = PersonRepository(db)
    event_repo = EventRepository(db)
    attendance_repo = AttendanceRepository(db)
    identifier_repository = IdentifierRepository(db)
    event_template_repo = EventTemplateRepository(db)

    person_service = PersonService(person_repo)
    event_service = EventService(event_repo)
    attendance_serivce = AttendanceService(attendance_repo, person_repo, event_repo)
    event_template_service = EventTemplateService(event_template_repo)

    view_model_factory = ViewModelFactory(
        attendance_service=attendance_serivce,
        person_service=person_service,
        event_service=event_service,
        event_template_service=event_template_service,
    )

    window = MainWindow(view_model_factory)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
