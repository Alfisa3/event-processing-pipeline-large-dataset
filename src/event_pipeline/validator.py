from pydantic import ValidationError

from event_pipeline.models import Event


def validate_event(data: dict) -> tuple[Event | None, str | None]:
    try:
        event = Event(**data)
        return event, None

    except (ValidationError, ValueError) as error:
        return None, str(error)