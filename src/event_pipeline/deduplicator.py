
from event_pipeline.models import Event


def remove_duplicates(
    events: list[Event],
) -> tuple[list[Event], int]:
    seen_event_ids: set[str] = set()
    unique_events: list[Event] = []
    duplicates = 0

    for event in events:
        if event.event_id in seen_event_ids:
            duplicates += 1
            continue

        seen_event_ids.add(event.event_id)
        unique_events.append(event)

    return unique_events, duplicates
