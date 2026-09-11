V1 Model — Basic API Contract Monitoring

A lightweight Python tool that detects API contract changes by comparing the current JSON response structure against a stored baseline.

Problem

An API can return HTTP 200 OK while silently changing the structure of its response.

For example, an API may change:

{
    "rate": 95.42,
    "date": "2026-09-11"
}

to:

{
    "exchange_rate": 95.42,
    "date": "2026-09-11"
}

The API is technically working, but an application expecting rate may fail.

API Contract Watchdog detects these structural changes before they cause unexpected application failures.

V1 Features
Fetches JSON data from an API
Extracts the response schema and data types
Creates and stores a baseline contract
Detects newly added fields
Detects removed fields
Detects data type changes
Classifies detected changes by severity
Automatically creates the baseline on the first run
How It Works
┌──────────────┐
│   Target API │
└──────┬───────┘
       ↓
┌──────────────┐
│ HTTP Request │
└──────┬───────┘
       ↓
┌──────────────┐
│ JSON Response│
└──────┬───────┘
       ↓
┌──────────────────┐
│ Schema Extraction│
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Baseline Compare │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Change Detection │
└──────┬───────────┘
       ↓
┌──────────────────┐
│ Severity Analysis│
└──────────────────┘
Example
Baseline
{
    "date": "str",
    "base": "str",
    "quote": "str",
    "rate": "float"
}

If the API changes the rate field from a float to a str, the watchdog reports:

API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: HIGH

Type changes:
  ~ rate: float → str

If a new field is added:

API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: LOW

Added fields:
  + timestamp

If a field is removed:

API CONTRACT WATCHDOG
---------------------
✗ API CONTRACT: CHANGED
Severity: HIGH

Removed fields:
  - rate
Severity Model
Detected Change	Severity	Reason
No change	OK	Contract remains stable
Field added	LOW	Existing consumers can usually ignore additional fields
Field removed	HIGH	Existing consumers may depend on the missing field
Data type changed	HIGH	Existing application logic may fail when processing the new type
Tech Stack
Python — Core implementation
Requests — HTTP/API communication
JSON — Baseline persistence
REST API — Data source
Project Structure
API-Contract-Watchdog/
│
├── watchdog.py
├── baseline.json
├── requirements.txt
├── .gitignore
└── README.md
File Responsibilities
File	Purpose
watchdog.py	Fetches the API, extracts the schema, compares contracts, and determines severity
baseline.json	Stores the expected API contract
requirements.txt	Lists Python dependencies
.gitignore	Prevents unnecessary files from being committed
README.md	Project documentation
Setup
1. Clone the repository
git clone <repository-url>
cd API-Contract-Watchdog
2. Install dependencies
pip install -r requirements.txt
3. Run the watchdog
python watchdog.py

On the first run, the watchdog creates the baseline automatically.

A healthy API contract produces:

API CONTRACT WATCHDOG
---------------------
✓ API CONTRACT: OK
Current API

V1 monitors the Frankfurter USD/INR exchange-rate endpoint:

https://api.frankfurter.dev/v2/rate/USD/INR

The endpoint is used as a practical API source for demonstrating contract monitoring.

V1 Scope

V1 focuses on deterministic API contract detection.

It currently compares:

Field names
Field presence
Python data types

It does not yet monitor:

Nested JSON structures
Multiple APIs
API response values
Historical changes
Email notifications
Scheduled monitoring
AI-generated explanations

Keeping these outside V1 keeps the core monitoring logic simple, testable, and deterministic.