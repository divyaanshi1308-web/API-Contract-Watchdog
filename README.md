# API Contract Watchdog

> **V1 Model — Basic API Contract Monitoring**

A lightweight Python tool that detects API contract changes by comparing the current JSON response structure against a stored baseline.

---

## Problem

An API can return **HTTP 200 OK** while silently changing the structure of its response.

For example, an API may change:

```json
{
    "rate": 95.42,
    "date": "2026-09-11"
}
````

to:

```json
{
    "exchange_rate": 95.42,
    "date": "2026-09-11"
}
```

The API is technically working, but an application expecting `rate` may fail.

**API Contract Watchdog detects these structural changes so developers can identify potential breaking changes before they affect applications.**

---

## V1 Features

* Fetches JSON data from an API
* Extracts the response schema and data types
* Creates and stores a baseline contract
* Detects newly added fields
* Detects removed fields
* Detects data type changes
* Classifies detected changes by severity
* Automatically creates the baseline on the first run

---

## How It Works

```text
Target API
    ↓
HTTP Request
    ↓
JSON Response
    ↓
Schema Extraction
    ↓
Baseline Comparison
    ↓
Change Detection
    ↓
Severity Analysis
```

---

## Example

### Baseline

```json
{
    "date": "str",
    "base": "str",
    "quote": "str",
    "rate": "float"
}
```

### Type Change

If the API changes the `rate` field from a `float` to a `str`:

```text
API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: HIGH

Type changes:
  ~ rate: float → str
```

### Added Field

If a new field is added:

```text
API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: LOW

Added fields:
  + timestamp
```

### Removed Field

If an existing field is removed:

```text
API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: HIGH

Removed fields:
  - rate
```

---

## Severity Model

| Detected Change   | Severity | Reason                                                           |
| ----------------- | -------- | ---------------------------------------------------------------- |
| No change         | `OK`     | Contract remains stable                                          |
| Field added       | `LOW`    | Existing consumers can usually ignore additional fields          |
| Field removed     | `HIGH`   | Existing consumers may depend on the missing field               |
| Data type changed | `HIGH`   | Existing application logic may fail when processing the new type |

---

## Tech Stack

* **Python** — Core implementation
* **Requests** — HTTP/API communication
* **JSON** — Baseline persistence
* **REST API** — Data source

---

## Project Structure & File Responsibilities

| File               | Purpose                                                                           |
| ------------------ | --------------------------------------------------------------------------------- |
| `watchdog.py`      | Fetches the API, extracts the schema, compares contracts, and determines severity |
| `baseline.json`    | Stores the expected API contract                                                  |
| `requirements.txt` | Lists Python dependencies                                                         |
| `.gitignore`       | Prevents unnecessary files from being committed                                   |
| `README.md`        | Project documentation                                                             |
---

## Author

**Divyaanshi Maheshwari**
