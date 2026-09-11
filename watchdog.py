import json
import hashlib
import requests
import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv
from datetime import datetime


CONFIG_FILE = "config.json"
BASELINE_FILE = "baseline.json"
HISTORY_FILE = "history.json"


load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
    print("✗ Email configuration is missing.")
    print("Please check your .env file.")
    exit()
    
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
    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return extract_schema(data)

    except requests.exceptions.Timeout:
        print("✗ API request timed out.")
        return None

    except requests.exceptions.RequestException as error:
        print(f"✗ API request failed: {error}")
        return None

    except ValueError:
        print("✗ API returned invalid JSON.")
        return None


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


def send_email_alert(subject, body):
    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = EMAIL_SENDER
    message["To"] = EMAIL_RECEIVER

    message.set_content(body)

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            EMAIL_SENDER,
            EMAIL_PASSWORD
        )

        server.send_message(message)

def should_send_alert(current_fingerprint):
    try:
        with open(HISTORY_FILE, "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        return True

    for entry in reversed(history):
        if entry["severity"] == "HIGH":
            return entry["fingerprint"] != current_fingerprint

    return True

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

if current_schema is None:
    exit()


# Generate current fingerprint
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

# Send alert before saving the current check
if severity == "HIGH" and should_send_alert(current_fingerprint):
    send_email_alert(
        "API Contract Watchdog - HIGH Severity Change",
        f"""
API contract change detected.

API:
{url}

Severity:
HIGH

Removed fields:
{removed}

Type changes:
{type_changed}

Current fingerprint:
{current_fingerprint}

Please review the API contract.
"""
    )
    print("✓ HIGH severity alert email sent successfully.")

# Save check history
status = "OK" if severity == "OK" else "CHANGED"

save_history(
    status,
    severity,
    current_fingerprint
)
        
# Display result
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