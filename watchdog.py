import json
import hashlib
import requests

from datetime import datetime

CONFIG_FILE = "config.json"
BASELINE_FILE = "baseline.json"
HISTORY_FILE = "history.json"


def load_config():
    with open(CONFIG_FILE, "r") as file:
        return json.load(file)


def extract_schema(data, prefix=""):
    schema = {}

    if isinstance(data, dict):

        for key, value in data.items():

            field_name = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                schema[field_name] = "dict"

                schema.update(
                    extract_schema(value, field_name)
                )

            elif isinstance(value, list):
                schema[field_name] = "list"

                if value:
                    schema.update(
                        extract_schema(
                            value[0],
                            f"{field_name}[]"
                        )
                    )

            else:
                schema[field_name] = type(value).__name__

    return schema


def get_api_schema(url):
    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

    return extract_schema(data)


def load_baseline():
    with open(BASELINE_FILE, "r") as file:
        return json.load(file)


def save_baseline(schema):
    with open(BASELINE_FILE, "w") as file:
        json.dump(schema, file, indent=4)

def save_history(status, severity, fingerprint):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "severity": severity,
        "fingerprint": fingerprint
    }

    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)

    except FileNotFoundError:
        history = []

    history.append(entry)

    with open(HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)
        
def generate_fingerprint(schema):
    schema_string = json.dumps(
        schema,
        sort_keys=True
    )

    return hashlib.sha256(
        schema_string.encode()
    ).hexdigest()


def compare_schemas(baseline, current):
    added = []
    removed = []
    type_changed = []

    for key in current:

        if key not in baseline:
            added.append(key)

        elif baseline[key] != current[key]:
            type_changed.append(
                (key, baseline[key], current[key])
            )

    for key in baseline:

        if key not in current:
            removed.append(key)

    return added, removed, type_changed


def determine_severity(added, removed, type_changed):

    if removed or type_changed:
        return "HIGH"

    if added:
        return "LOW"

    return "OK"


# Load API configuration
config = load_config()
url = config["url"]


# Fetch current API schema
current_schema = get_api_schema(url)

current_fingerprint = generate_fingerprint(
    current_schema
)


# First run
try:
    baseline_schema = load_baseline()

except FileNotFoundError:

    save_baseline(current_schema)

    print("API CONTRACT WATCHDOG")
    print("---------------------")
    print("✓ First run detected")
    print("✓ Baseline created successfully")
    print(f"Fingerprint: {current_fingerprint}")

    exit()


# Generate baseline fingerprint
baseline_fingerprint = generate_fingerprint(
    baseline_schema
)


# Compare current API with baseline
added, removed, type_changed = compare_schemas(
    baseline_schema,
    current_schema
)


# Determine severity
severity = determine_severity(
    added,
    removed,
    type_changed
)

status = "OK" if severity == "OK" else "CHANGED"

save_history(
    status,
    severity,
    current_fingerprint
)

print("API CONTRACT WATCHDOG")
print("---------------------")

print(f"Baseline fingerprint: {baseline_fingerprint}")
print(f"Current fingerprint:  {current_fingerprint}")


if severity == "OK":

    print("\n✓ API CONTRACT: OK")

else:

    print("\n✗ API CONTRACT: CHANGED")
    print(f"Severity: {severity}")

    if added:

        print("\nAdded fields:")

        for field in added:
            print(f"  + {field}")

    if removed:

        print("\nRemoved fields:")

        for field in removed:
            print(f"  - {field}")

    if type_changed:

        print("\nType changes:")

        for field, old_type, new_type in type_changed:

            print(
                f"  ~ {field}: "
                f"{old_type} → {new_type}"
            )