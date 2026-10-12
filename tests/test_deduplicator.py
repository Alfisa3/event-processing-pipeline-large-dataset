
from event_pipeline.deduplicator import remove_duplicates
from event_pipeline.models import Event


def test_remove_duplicates():
    event1 = Event(
        event_id="e1001",
        event_time="2019-10-01 00:00:00 UTC",
        event_type="view",
        product_id=100,
        category_id=200,
        category_code="electronics",
        brand="branda",
        price="50.00",
        user_id=501,
        user_session="session1",
    )

    event2 = Event(
        event_id="e1001",
        event_time="2019-10-01 00:00:00 UTC",
        event_type="view",
        product_id=100,
        category_id=200,
        category_code="electronics",
        brand="branda",
        price="50.00",
        user_id=501,
        user_session="session1",
    )

    event3 = Event(
        event_id="e1002",
        event_time="2019-10-01 00:01:00 UTC",
        event_type="cart",
        product_id=101,
        category_id=200,
        category_code="electronics",
        brand="branda",
        price="75.00",
        user_id=502,
        user_session="session2",
    )

    unique_events, duplicates = remove_duplicates(
        [event1, event2, event3]
    )

    assert len(unique_events) == 2
    assert duplicates == 1
    assert [event.event_id for event in unique_events] == [
        "e1001",
        "e1002",
    ]
