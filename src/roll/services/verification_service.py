"""Verification service for checking identifiers."""

import logging
from typing import override, Optional

from roll.core import IIdentifierRepository, IVerificationService

logger = logging.getLogger(__name__)


class VerificationService(IVerificationService):
    def __init__(self, identifier_repo: IIdentifierRepository):
        self.identifier_repo = identifier_repo
        logger.info("Initialized verification service")

    @override
    def verify_hash(self, hash_value: str) -> Optional[int]:
        """Check if hash exists in repository and return person_id."""
        identifier = self.identifier_repo.get_by_hash(hash_value)
        if identifier:
            return identifier.person_id
        return None