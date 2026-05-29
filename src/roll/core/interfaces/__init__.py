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
    IEventTemplateRepository,
    IIdentifierRepository,
    IPersonRepository,
)
from roll.core.interfaces.services import (
    IAttendanceService,
    IEventService,
    IEventTemplateService,
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
    "IEventTemplateRepository",
    "IEventTemplateService",
    "IIdentifierReaderService",
    "IIdentifierRepository",
    "IIdentifierService",
    "IPersonRepository",
    "IPersonService",
    "IVerificationService",
]
