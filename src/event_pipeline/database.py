
import sqlite3
from pathlib import Path

from event_pipeline.models import Event


def create_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_time TEXT NOT NULL,
            event_type TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            category_code TEXT,
            brand TEXT,
            price TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            user_session TEXT NOT NULL
        )
        """
    )

    connection.execute("DELETE FROM events")
    connection.commit()

    return connection


def insert_events(
    connection: sqlite3.Connection,
    events: list[Event],
) -> int:
    inserted = 0

    for event in events:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO events (
                event_id,
                event_time,
                event_type,
                product_id,
                category_id,
                category_code,
                brand,
                price,
                user_id,
                user_session
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_time.isoformat(),
                event.event_type,
                event.product_id,
                event.category_id,
                event.category_code,
                event.brand,
                str(event.price),
                event.user_id,
                event.user_session,
            ),
        )

        inserted += cursor.rowcount

    connection.commit()
    return inserted
