# Event Processing & Analytics Pipeline

## Overview

The **Event Processing & Analytics Pipeline** is a Python application designed to process large volumes of e-commerce event data from CSV and JSON files. It validates incoming records, identifies duplicate events, stores cleaned data in an SQLite database, performs analytics, and generates reports in JSON and CSV formats.

The project demonstrates data processing, validation, database management, analytics, and automated testing using Python.

## Features

- **CSV and JSON Support:** Read event data from CSV and JSON files.
- **Data Validation:** Validate event records using Pydantic.
- **Data Cleaning:** Normalize event fields and timestamps.
- **Duplicate Detection:** Identify duplicate records using generated event identifiers.
- **SQLite Database:** Store validated event records in a database.
- **Data Analytics:** Calculate event statistics, unique users, popular brands, top users, and hourly activity.
- **Report Generation:** Generate JSON and CSV reports.
- **Invalid Record Tracking:** Save invalid records separately for inspection.
- **Logging:** Track processing activities and errors.
- **Automated Testing:** Use pytest to verify application functionality.
- **Code Quality:** Use Ruff to check code style and potential issues.
- **Large Dataset Processing:** Process and analyze hundreds of thousands of records.

## Technology Stack

- **Python 3.14.x** — Core programming language
- **uv** — Python project and dependency management
- **Pydantic** — Data validation
- **SQLite** — Database storage
- **pathlib** — File and directory path handling
- **csv and json** — Data input and report generation
- **pytest** — Automated testing
- **Ruff** — Code quality and linting

## Project Structure

```text
event-processing-pipeline/
│
├── data/
│   ├── input/
│   ├── output/
│   └── events.db
│
├── src/
│   └── event_pipeline/
│       ├── __init__.py
│       ├── main.py
│       ├── models.py
│       ├── validator.py
│       ├── deduplicator.py
│       ├── database.py
│       ├── analytics.py
│       └── reporter.py
│
├── tests/
│
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

*Note: The structure above represents the main project components. The exact files and directories may vary depending on your implementation.*

## Processing Workflow

The application follows these processing stages:

```text
Input CSV / JSON
       |
       v
Text and Record Reading
       |
       v
Data Validation
       |
       v
Data Cleaning and Normalization
       |
       v
Duplicate Detection
       |
       v
SQLite Database Storage
       |
       v
Analytics and Statistics
       |
       v
JSON and CSV Reports
```

### Processing Steps

1. **Input:** Read e-commerce event records from a CSV or JSON file.
2. **Validation:** Validate the records and reject invalid data.
3. **Cleaning:** Normalize relevant text fields and timestamps.
4. **Deduplication:** Identify duplicate records using generated event identifiers.
5. **Storage:** Save cleaned records in an SQLite database.
6. **Analytics:** Calculate statistics such as event counts, unique users, purchase counts, top brands, and hourly activity.
7. **Reporting:** Generate reports containing analytics results and processing summaries.

## Dataset

The application supports e-commerce event data containing fields such as:

| Field | Description |
|---|---|
| `event_time` | Date and time of the event |
| `event_type` | Type of activity, such as view, cart, or purchase |
| `product_id` | Product identifier |
| `category_id` | Product category identifier |
| `category_code` | Product category information |
| `brand` | Product brand |
| `price` | Product price |
| `user_id` | User identifier |
| `user_session` | User session identifier |

The application generates an event identifier because the sample e-commerce dataset does not provide an `event_id` field.

## Installation and Setup

### Prerequisites

Install the following:

- Python 3.14.x
- uv
- Git (optional, for version control)

### 1. Clone the Repository

```bash
git clone https://github.com/Alfisa3/event-processing-pipeline-large-dataset.git
```

### 2. Navigate to the Project Directory

```bash
cd event-processing-pipeline-large-dataset
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

### Process a CSV File

Place your input dataset in an accessible location and run:

```bash
uv run python -m event_pipeline.main "data/input/test_events.csv"
```

Replace the example filename with the path to your input CSV file.

### Process a Large Dataset

Example command for a dataset stored on your computer:

```bash
uv run python -m event_pipeline.main "C:\path\to\your\dataset.csv"
```

Replace the path with the actual location of your dataset.

### Output Files

After successful processing, the application generates reports in the `data/output/` directory.

| File | Purpose |
|---|---|
| `report.json` | Detailed analytics and processing summary in JSON format |
| `report.csv` | Analytics results in CSV format |
| `invalid_records.csv` | Records that failed validation |

The SQLite database is stored at `data/events.db`.

## Analytics

The application calculates statistics such as:

- Total records received
- Number of valid records
- Number of invalid records
- Number of duplicate records
- Number of unique users
- Total purchase events
- Estimated purchase value
- Event counts by type
- Top brands and users
- Hourly event activity
- Total processing time

The available statistics depend on the fields present in the input dataset.

## Testing

Run the automated test suite:

```bash
uv run pytest
```

### Code Quality Check

Run Ruff to check the project for linting issues:

```bash
uv run ruff check .
```

### Check Python Version

```bash
uv run python --version
```

## Performance Testing

The application was tested with both a small sample dataset and a larger e-commerce dataset containing **350,000 records**.

Example results from a large-dataset run:

| Metric | Result |
|---|---:|
| Records received | 350,000 |
| Valid records | 350,000 |
| Invalid records | 0 |
| Duplicate records | 175 |
| Unique users | 64,521 |
| Purchase events | 6,632 |
| Processing time | Approximately 44 seconds |

*These results are from a previous test run. Actual processing time and statistics may vary depending on the dataset and system performance.*

## Important Notes

- The input dataset should contain the required event fields.
- The current implementation generates event identifiers from row contents when the source data does not provide an `event_id`.
- Identical rows can be detected as duplicates, but this approach may not identify semantically repeated events whose row contents differ.
- The example dataset does not contain a dedicated `source` field, so source-based analytics are not available unless that field is added.
- The database is recreated during processing in the current implementation, so previously stored records may be replaced when a new dataset is processed.
- Large input datasets and generated output files should remain local and should not be committed to GitHub unnecessarily.

## Future Improvements

- Support configurable database persistence without recreating existing tables.
- Improve duplicate detection using reliable event identifiers.
- Add source-based analytics when source information is available.
- Improve memory efficiency when processing large JSON files.
- Add configurable logging levels and processing options.
- Add more comprehensive validation and integration tests.
- Introduce command-line options for selecting input and output paths.

## Learning Outcomes

This project provided practical experience with:

- Python application development
- Data validation and cleaning
- CSV and JSON processing
- SQLite database operations
- Data analytics and report generation
- Large dataset processing
- Automated testing with pytest
- Code quality checks with Ruff
- Dependency management using uv

## Author

**Alfisa Nazar**

GitHub: [Alfisa3](https://github.com/Alfisa3)

## License

This project is intended for learning and demonstration purposes. Add a license file if you plan to distribute the project under specific reuse terms.