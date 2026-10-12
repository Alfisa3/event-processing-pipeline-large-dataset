
from event_pipeline.database import create_database, insert_events
from event_pipeline.models import Event


def test_insert_events(tmp_path):
    db_path = tmp_path / "test.db"
    connection = create_database(db_path)

    event = Event(
        event_id="e1001",
        event_time="2019-10-01 00:00:00 UTC",
        event_type="view",
        product_id=100,
        category_id=200,
        category_code="electronics",
        brand="branda",
        price="50.00",
        user_id=601,
        user_session="session1",
    )

    try:
        inserted = insert_events(connection, [event])

        assert inserted == 1

        count = connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        assert count == 1

    finally:
        connection.close()


def test_duplicate_event_id_is_ignored(tmp_path):
    db_path = tmp_path / "test.db"
    connection = create_database(db_path)

    event = Event(
        event_id="e1001",
        event_time="2019-10-01 00:00:00 UTC",
        event_type="view",
        product_id=100,
        category_id=200,
        category_code="electronics",
        brand="branda",
        price="50.00",
        user_id=601,
        user_session="session1",
    )

    try:
        first_inserted = insert_events(connection, [event])
        second_inserted = insert_events(connection, [event])

        assert first_inserted == 1
        assert second_inserted == 0

        count = connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        assert count == 1

    finally:
        connection.close()
