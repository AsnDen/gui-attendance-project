import logging
from datetime import time
from typing import TYPE_CHECKING, override

from roll.core import (
    BaseEventTemplate,
    EventTemplateUpdateDTO,
    IEventTemplateRepository,
    IEventTemplateService,
)
from roll.services.exceptions import (
    EmptyLabelError,
    EventTemplateNotFoundError,
    ZeroDurationError,
)

if TYPE_CHECKING:
    from datetime import timedelta

logger = logging.getLogger(__name__)


class EventTemplateService(IEventTemplateService):
    def __init__(self, repo: IEventTemplateRepository) -> None:
        """Initializes event service with event repository."""
        self.repo: IEventTemplateRepository = repo
        logger.info("Initialized event service")

    @override
    def add_template(
        self,
        label: str,
        start_time: time,
        duration: timedelta,
        description: str = "",
    ) -> int:
        if label == "":
            raise EmptyLabelError

        if duration.total_seconds() == 0:
            raise ZeroDurationError

        template = EventTemplateUpdateDTO(
            label=label,
            start_time=start_time,
            duration=duration,
            description=description,
        )
        return self.repo.add(template)

    @override
    def get_template(self, event_template_id: int) -> BaseEventTemplate:
        template = self.repo.get(event_template_id)

        if template is None:
            raise EventTemplateNotFoundError

        return template

    @override
    def get_all_templates(self) -> tuple[BaseEventTemplate, ...]:
        return self.repo.get_all()

    @override
    def update_template(
        self,
        event_template_id: int,
        *,
        label: str | None = None,
        start_time: time | None = None,
        duration: timedelta | None = None,
        description: str | None = None,
    ) -> None:
        if label == "":
            raise EmptyLabelError

        if duration is not None and duration.total_seconds() == 0:
            raise ZeroDurationError

        template = EventTemplateUpdateDTO(
            label=label,
            start_time=start_time,
            duration=duration,
            description=description,
        )
        self.repo.update(event_template_id, template)

    @override
    def delete_template(self, event_template_id: int) -> None:
        if not self.repo.delete(event_template_id):
            raise EventTemplateNotFoundError
