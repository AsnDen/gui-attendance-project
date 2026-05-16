from abc import ABC

from PySide6.QtSql import QSqlQuery

from roll.repositories.exceptions import (
    QueryFailedExecError,
    QueryFailedPrepareError,
)


class BaseQtSQLiteRepository(ABC):
    """Provides raising error methods."""

    @staticmethod
    def _raise_on_prepare(query: QSqlQuery) -> None:
        """Should be userd in case query.prepare() error."""
        error = query.lastError().text()
        raise QueryFailedPrepareError(error)

    @staticmethod
    def _raise_on_exec(query: QSqlQuery) -> None:
        """Should be userd in case query.exec() error."""
        error = query.lastError().text()
        raise QueryFailedExecError(error)