
from event_pipeline.validator import validate_event


def test_valid_event():
    data = {
        "event_id": "e1001",
        "event_time": "2019-10-01 00:00:00 UTC",
        "event_type": "view",
        "product_id": 100,
        "category_id": 200,
        "category_code": "electronics",
        "brand": "branda",
        "price": "50.00",
        "user_id": 501,
        "user_session": "session1",
    }

    event, error = validate_event(data)

    assert event is not None
    assert error is None
    assert event.event_id == "e1001"


def test_invalid_event():
    data = {
        "event_id": "e1002",
        "event_time": "2019-10-01 00:00:00 UTC",
        "event_type": "unknown_event",
        "product_id": 100,
        "category_id": 200,
        "category_code": "electronics",
        "brand": "branda",
        "price": "50.00",
        "user_id": 501,
        "user_session": "session1",
    }

    event, error = validate_event(data)

    assert event is None
    assert error is not None
