import csv
import json
from pathlib import Path


def read_events(file_path: Path):
    if file_path.suffix.lower() == ".json":
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    if file_path.suffix.lower() == ".csv":
        with file_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            yield from reader

        return

    raise ValueError("Unsupported file format")