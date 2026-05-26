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
from roll.services import AttendanceService, EventService, PersonService


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

    person_service = PersonService(person_repo)
    event_service = EventService(event_repo)
    attendance_serivce = AttendanceService(attendance_repo, person_repo, event_repo)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
