class PersonNotFoundError(Exception):
    pass


class AttendanceNotFoundError(Exception):
    pass


class EventNotFoundError(Exception):
    pass


class EmptyLabelError(Exception):
    pass


class ZeroDurationError(Exception):
    pass


<<<<<<< HEAD
class QueryFailedPrepareError(Exception):
    pass


class QueryFailedExecError(Exception):
    pass


class DTOValueError(Exception):
    pass


class CameraUnavailableError(Exception):
    """Raised when camera cannot be opened or is not available."""


class FrameCaptureError(Exception):
    """Raised when frame capture fails."""


class QRReaderError(Exception):
    """Base QR reader exception."""


class IdentifierNotFoundError(Exception):
    """Raised when identifier does not exist."""
=======
class EventTemplateNotFoundError(Exception):
    pass
>>>>>>> upstream/ui
