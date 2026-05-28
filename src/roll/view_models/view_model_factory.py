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
    ):
        self._attendance_service = attendance_service
        self._event_service = event_service
        self._person_service = person_service
        self._event_template_service = event_template_service

    def create_calendar_view_model(self) -> CalendarPanelViewModel:
        return CalendarPanelViewModel(self._event_service, self._event_template_service)

    @property
    def event_service(self) -> IEventService:
        return self._event_service
