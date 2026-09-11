import json
import requests

URL = "https://api.frankfurter.dev/v2/rate/USD/INR"
BASELINE_FILE = "baseline.json"


def get_api_schema():
    response = requests.get(URL)
    response.raise_for_status()

    data = response.json()

    schema = {}

    for key, value in data.items():
        schema[key] = type(value).__name__

    return schema


def load_baseline():
    with open(BASELINE_FILE, "r") as file:
        return json.load(file)


def save_baseline(schema):
    with open(BASELINE_FILE, "w") as file:
        json.dump(schema, file, indent=4)


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


current_schema = get_api_schema()

# First run
try:
    baseline_schema = load_baseline()

except FileNotFoundError:
    save_baseline(current_schema)

    print("API CONTRACT WATCHDOG")
    print("---------------------")
    print("✓ First run detected")
    print("✓ Baseline created successfully")

    exit()


# Compare current API with baseline
added, removed, type_changed = compare_schemas(
    baseline_schema,
    current_schema
)

severity = determine_severity(
    added,
    removed,
    type_changed
)

print("API CONTRACT WATCHDOG")
print("---------------------")

if severity == "OK":
    print("✓ API CONTRACT: OK")

else:
    print(f"✗ API CONTRACT: CHANGED")
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