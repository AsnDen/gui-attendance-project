import logging
import sys

from PySide6.QtWidgets import QApplication

from roll.core import init_database, setup_logging
from roll.repositories import (
    AttendanceRepository,
    EventRepository,
    IdentifierRepository,
    PersonRepository,
)
from roll.services import (
    AttendanceService,
    EventService,
    PersonService,
    IdentifierService,
)
from roll.ui import MainWindow
from roll.view_models import ViewModelFactory


def main() -> None:
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
    identifier_repo = IdentifierRepository(db)

    person_service = PersonService(person_repo)
    event_service = EventService(event_repo)
    attendance_service = AttendanceService(attendance_repo, person_repo, event_repo)
    identifier_service = IdentifierService(identifier_repo, person_repo)

    view_model_factory = ViewModelFactory(
        attendance_service=attendance_service,
        event_service=event_service,
        person_service=person_service,
        identifier_service=identifier_service,
    )

    window = MainWindow(
        view_model_factory=view_model_factory,
        attendance_service=attendance_service,
        person_service=person_service,
        identifier_service=identifier_service,
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()