"""Interfaces for services and repositories.

Provides:
    IAttendanceRepository
    IEventRepository
    IIdentifierRepository
    IPersonRepository
"""

from roll.core.interfaces.repositories import (
    IAttendanceRepository,
    IEventRepository,
    IIdentifierRepository,
    IPersonRepository,
)
from roll.core.interfaces.services import (
    IAttendanceService,
    IEventService,
    IIdentifierReaderService,
    IIdentifierService,
    IPersonService,
    IVerificationService,
)

__all__ = [
    "IAttendanceRepository",
    "IAttendanceService",
    "IEventRepository",
    "IEventService",
    "IIdentifierReaderService",
    "IIdentifierRepository",
    "IIdentifierService",
    "IPersonRepository",
    "IPersonService",
    "IVerificationService",
]
