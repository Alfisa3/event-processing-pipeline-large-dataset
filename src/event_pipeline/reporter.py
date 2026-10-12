import csv
import json
from pathlib import Path


def save_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)


def save_csv_report(report: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])

        for key, value in report.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            writer.writerow([key, value])