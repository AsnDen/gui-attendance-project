from roll.core import (
    IAttendanceService,
    IEventService,
    IPersonService,
)
from roll.view_models.calendar_view_model import CalendarPanelViewModel


class ViewModelFactory:
    def __init__(
        self,
        *,
        attendance_service: IAttendanceService,
        event_service: IEventService,
        person_service: IPersonService,
        # identifier_service: IIdentifierService,
        # identifier_reader_service: IIdentifierReaderService,
        # verification_service: IVerificationService,
    ):
    
        self._attendance_service = attendance_service
        self._event_service = event_service
        self._person_service = person_service
        self._identifier_service = identifier_service

    def create_calendar_view_moder(self) -> CalendarPanelViewModel:
        return CalendarPanelViewModel(self._event_service)

    @property
    def event_service(self) -> IEventService:
        return self._event_service