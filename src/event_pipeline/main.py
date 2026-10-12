
import csv
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from event_pipeline.logger import setup_logger
from event_pipeline.reporter import save_csv_report, save_report
from event_pipeline.validator import validate_event

BATCH_SIZE = 10_000

REQUIRED_COLUMNS = {
    "event_time",
    "event_type",
    "product_id",
    "category_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
}


def generate_event_id(row: dict[str, Any]) -> str:
    """Create a stable ID because the Kaggle dataset has no event_id."""
    normalized_row = {
        key: "" if value is None else str(value).strip()
        for key, value in row.items()
    }
    row_json = json.dumps(
        normalized_row,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(row_json.encode("utf-8")).hexdigest()


def read_events(input_path: Path):
    """Read CSV rows or records from a JSON array."""
    if input_path.suffix.lower() == ".csv":
        with input_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.DictReader(file)

            if not reader.fieldnames or not REQUIRED_COLUMNS.issubset(
                set(reader.fieldnames)
            ):
                raise ValueError(
                    "CSV headers do not match the expected Kaggle columns"
                )

            yield from reader

    elif input_path.suffix.lower() == ".json":
        with input_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                "JSON input must contain an array of event objects"
            )

        for row in data:
            if not isinstance(row, dict):
                raise TypeError(
                    "Every JSON array item must be an event object"
    )
            yield row

    else:
        raise ValueError("Unsupported file format. Use CSV or JSON.")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: uv run python -m event_pipeline.main <input.csv|input.json>"
        )

    input_path = Path(sys.argv[1])

    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    logger = setup_logger()
    start = time.perf_counter()

    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    invalid_path = output_dir / "invalid_records.csv"
    db_path = Path("data/events.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)

    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        connection.execute("PRAGMA temp_store=FILE")
        connection.execute("PRAGMA cache_size=-64000")

        # Start with a fresh database table for each run.
        connection.execute("DROP TABLE IF EXISTS events")
        connection.execute(
            """
            CREATE TABLE events (
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
        connection.commit()

        received = 0
        valid = 0
        invalid = 0
        duplicates = 0

        with invalid_path.open(
            "w", encoding="utf-8", newline=""
        ) as invalid_file:
            invalid_writer = csv.writer(invalid_file)
            invalid_writer.writerow(["row_data", "error"])

            batch = []

            for row in read_events(input_path):
                received += 1

                if received % 100_000 == 0:
                    logger.info("Processed %s records...", received)

                # The Kaggle dataset does not provide event_id.
                row_with_id = {
                    **row,
                    "event_id": generate_event_id(row),
                }

                event, error = validate_event(row_with_id)

                if error:
                    invalid += 1
                    invalid_writer.writerow(
                        [
                            json.dumps(row, ensure_ascii=False),
                            error,
                        ]
                    )
                    continue

                valid += 1

                batch.append(
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
                    )
                )

                if len(batch) >= BATCH_SIZE:
                    before = connection.total_changes

                    connection.executemany(
                        """
                        INSERT OR IGNORE INTO events VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                        """,
                        batch,
                    )

                    inserted = connection.total_changes - before
                    duplicates += len(batch) - inserted
                    connection.commit()
                    batch.clear()

            if batch:
                before = connection.total_changes

                connection.executemany(
                    """
                    INSERT OR IGNORE INTO events VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    batch,
                )

                inserted = connection.total_changes - before
                duplicates += len(batch) - inserted
                connection.commit()

        total_events = connection.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]

        unique_users = connection.execute(
            "SELECT COUNT(DISTINCT user_id) FROM events"
        ).fetchone()[0]

        total_purchases = connection.execute(
            """
            SELECT COUNT(*) FROM events
            WHERE event_type = 'purchase'
            """
        ).fetchone()[0]

        revenue = connection.execute(
            """
            SELECT COALESCE(SUM(CAST(price AS REAL)), 0)
            FROM events
            WHERE event_type = 'purchase'
            """
        ).fetchone()[0]

        events_by_type = dict(
            connection.execute(
                """
                SELECT event_type, COUNT(*)
                FROM events
                GROUP BY event_type
                ORDER BY event_type
                """
            ).fetchall()
        )

        # This is an e-commerce dataset, so brand analytics are useful.
        top_brands = [
            {"brand": brand or "unknown", "event_count": count}
            for brand, count in connection.execute(
                """
                SELECT brand, COUNT(*)
                FROM events
                GROUP BY brand
                ORDER BY COUNT(*) DESC
                LIMIT 10
                """
            ).fetchall()
        ]

        top_users = [
            {"user_id": user_id, "event_count": count}
            for user_id, count in connection.execute(
                """
                SELECT user_id, COUNT(*)
                FROM events
                GROUP BY user_id
                ORDER BY COUNT(*) DESC, user_id
                LIMIT 10
                """
            ).fetchall()
        ]

        hourly_activity = [
            {"hour": hour, "event_count": count}
            for hour, count in connection.execute(
                """
                SELECT substr(event_time, 12, 2), COUNT(*)
                FROM events
                GROUP BY 1
                ORDER BY 1
                """
            ).fetchall()
        ]

        report = {
            "input_file": input_path.name,
            "records_received": received,
            "valid": valid,
            "invalid": invalid,
            "duplicates": duplicates,
            "total_events": total_events,
            "unique_users": unique_users,
            "total_purchases": total_purchases,
            "estimated_purchase_value": round(revenue, 2),
            "events_by_type": events_by_type,
            "top_brands": top_brands,
            "top_active_users": top_users,
            "hourly_activity": hourly_activity,
            "processing_time_seconds": round(
                time.perf_counter() - start, 4
            ),
        }

        save_report(report, output_dir / "report.json")
        save_csv_report(report, output_dir / "report.csv")

        logger.info("Records received: %s", received)
        logger.info("Valid records: %s", valid)
        logger.info("Invalid records: %s", invalid)
        logger.info("Duplicates: %s", duplicates)
        logger.info("Unique users: %s", unique_users)
        logger.info("Total purchases: %s", total_purchases)
        logger.info(
            "Processing time: %s seconds",
            report["processing_time_seconds"],
        )

        print("\nProcessing completed!")
        print("-----------------------------")
        print(f"Records received : {received}")
        print(f"Valid records    : {valid}")
        print(f"Invalid records  : {invalid}")
        print(f"Duplicates       : {duplicates}")
        print(f"Unique users     : {unique_users}")
        print(f"Total purchases  : {total_purchases}")
        print(
            f"Processing time  : "
            f"{report['processing_time_seconds']} seconds"
        )
        print("Reports saved in data/output/")
        print(f"Invalid rows saved to {invalid_path}")

    except Exception:
        logger.exception("Pipeline failed")
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
