# API Contract Watchdog

> **V2 Model — Advanced API Contract Monitoring**

## V2 Features

- Fetches JSON data from a configurable API endpoint
- Extracts nested JSON structures
- Detects fields inside nested objects
- Detects fields inside arrays
- Generates SHA-256 schema fingerprints
- Compares the current contract against a stored baseline
- Detects added, removed, and type-changed fields
- Classifies detected changes by severity
- Maintains local change history
- Automatically creates the baseline on the first run

---

## Project Structure & File Responsibilities

| File | Purpose |
|---|---|
| `watchdog.py` | Fetches the API, extracts the schema, generates fingerprints, compares contracts, and determines severity |
| `baseline.json` | Stores the expected API contract |
| `config.json` | Stores the target API configuration |
| `history.json` | Stores local runtime history of API contract checks |
| `requirements.txt` | Lists Python dependencies |
| `.gitignore` | Prevents unnecessary and runtime-generated files from being committed |
| `README.md` | Project documentation |

---

## Author

**Divyaanshi Maheshwari**