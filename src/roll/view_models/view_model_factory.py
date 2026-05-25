from roll.core import (
    IAttendanceService,
    ICalendarPanelViewModel,
    IEventService,
    IPersonService,
)


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
        self._attendance_service: IAttendanceService = attendance_service
        self._event_service: IEventService = event_service
        self._person_service: IPersonService = person_service
        # self._identifier_service: IIdentifierService = identifier_service
        # self._identifier_reader_service: IIdentifierReaderService = (
        #     identifier_reader_service
        # )
        # self._verification_service: IVerificationService = verification_service

    def create_calendar_view_moder(self) -> ICalendarPanelViewModel:
        pass
