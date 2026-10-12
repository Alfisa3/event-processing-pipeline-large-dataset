def get_total_events(connection):
    result = connection.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()
    return result[0]


def get_unique_users(connection):
    result = connection.execute(
        "SELECT COUNT(DISTINCT user_id) FROM events"
    ).fetchone()
    return result[0]


def get_total_purchases(connection):
    result = connection.execute(
        """
        SELECT COUNT(*)
        FROM events
        WHERE event_type = 'purchase'
        """
    ).fetchone()
    return result[0]


def get_events_by_type(connection):
    rows = connection.execute(
        """
        SELECT event_type, COUNT(*)
        FROM events
        GROUP BY event_type
        ORDER BY event_type
        """
    ).fetchall()
    return dict(rows)


def get_events_by_brand(connection, limit=10):
    rows = connection.execute(
        """
        SELECT COALESCE(brand, 'unknown') AS brand, COUNT(*)
        FROM events
        GROUP BY brand
        ORDER BY COUNT(*) DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    return [
        {"brand": brand, "event_count": count}
        for brand, count in rows
    ]


def get_top_active_users(connection, limit=10):
    rows = connection.execute(
        """
        SELECT user_id, COUNT(*) AS event_count
        FROM events
        GROUP BY user_id
        ORDER BY event_count DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    return [
        {"user_id": user_id, "event_count": count}
        for user_id, count in rows
    ]


def get_hourly_activity(connection):
    rows = connection.execute(
        """
        SELECT substr(event_time, 12, 2) AS hour, COUNT(*)
        FROM events
        GROUP BY hour
        ORDER BY hour
        """
    ).fetchall()

    return [
        {"hour": hour, "event_count": count}
        for hour, count in rows
    ]


def get_total_revenue(connection):
    result = connection.execute(
        """
        SELECT COALESCE(SUM(CAST(price AS REAL)), 0)
        FROM events
        WHERE event_type = 'purchase'
        """
    ).fetchone()

    return round(result[0], 2)