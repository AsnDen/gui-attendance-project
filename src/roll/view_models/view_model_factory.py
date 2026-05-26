from roll.core import (
    IAttendanceService,
    IEventService,
    IEventTemplateService,
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
        event_template_service: IEventTemplateService,
        # identifier_service: IIdentifierService,
        # identifier_reader_service: IIdentifierReaderService,
        # verification_service: IVerificationService,
    ):
        self._attendance_service: IAttendanceService = attendance_service
        self._event_service: IEventService = event_service
        self._person_service: IPersonService = person_service
        self._event_template_serivce: IEventTemplateService = event_template_service
        # self._identifier_service: IIdentifierService = identifier_service
        # self._identifier_reader_service: IIdentifierReaderService = (
        #     identifier_reader_service
        # )
        # self._verification_service: IVerificationService = verification_service

    def create_calendar_view_moder(self) -> CalendarPanelViewModel:
        return CalendarPanelViewModel(self._event_service, self._event_template_serivce)
