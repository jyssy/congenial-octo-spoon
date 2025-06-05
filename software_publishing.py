#!/usr/local/nagios/venv/bin/python3
import requests, json, sys
from datetime import datetime
from dateutil import parser
import pytz

try:
    # API
    software_endpoint = "https://operations-api.access-ci.org/wh2/state/v1/status/?format=json"

    # Make the request
    try:
        response = requests.get(software_endpoint)
    except requests.exceptions.ConnectionError as e:
        print(f"CRITICAL: Connection error: {str(e)}")
        sys.exit(2)
    except requests.exceptions.Timeout as e:
        print(f"CRITICAL: Request timed out: {str(e)}")
        sys.exit(2)

    # Check if request was successful
    if response.status_code != 200:
        print(f"CRITICAL: API returned status code {response.status_code}")
        sys.exit(2)

    # Parse the JSON
    try:
        response_data = json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"WARNING: Invalid JSON response: {str(e)}")
        sys.exit(1)

    status_code = response.status_code
    current_date = datetime.now(pytz.UTC)
    max_age_days = 14

    # Function to check if a date is within threshold
    def is_recent(date_str, max_days):
        if not date_str:
            return False
        try:
            # Parse the date string to datetime object
            process_date = parser.parse(date_str)
            # Ensure timezone awareness
            if process_date.tzinfo is None:
                process_date = pytz.UTC.localize(process_date)
            # Calculate days difference
            days_diff = (current_date - process_date).days
            return days_diff <= max_days
        except:
            return False

    # Process records and check dates
    results = {
        "pass": [],
        "fail": [],
        "skipped": []
    }

    for record in response_data.get("record_list", []):
        record_id = record.get("ID")
        topic = record.get("Topic", "")

        # Skip if Topic is not exactly "glue2.applications"
        if topic != "glue2.applications":
            results["skipped"].append({
                "id": record_id,
                "reason": f"Topic '{topic}' is not 'glue2.applications'",
                "days_ago": "N/A"
            })
            continue

        # Skip if ID contains "test" (case-insensitive)
        if record_id and "test" in record_id.lower():
            results["skipped"].append({
                "id": record_id,
                "reason": "ID contains 'test'",
                "days_ago": "N/A"
            })
            continue

        # Skip if ID contains "test" (case-insensitive)
        if record_id and "test" in record_id.lower():
            results["skipped"].append({
                "id": record_id,
                "reason": "ID contains 'test'"
            })
            continue

        processing_start = record.get("ProcessingStart")
        processing_end = record.get("ProcessingEnd")

        # Check if the record is recent (using end date if available, otherwise start date)
        date_to_check = processing_end if processing_end else processing_start
        if is_recent(date_to_check, max_age_days):
            results["pass"].append({
                "id": record_id,
                "date": date_to_check,
                "days_ago": (current_date - parser.parse(date_to_check)).days
            })
        else:
            results["fail"].append({
                "id": record_id,
                "date": date_to_check,
                "days_ago": (current_date - parser.parse(date_to_check)).days if date_to_check else "unknown"
            })

    # Print summary
    if len(results['fail']) > 0:
        print(f"FAILED: {len(results['fail'])} resources have published software more than {max_age_days} days ago")

        # Print only the failed records
        print("\nFailed Checks: \n")
        for record in results["fail"]:
            print(f"  - {record['id']} published: ({record['days_ago']} days ago)")

        # Print skipped records
        print("\n The following items were skipped: \n")
        for record in results["skipped"]:
            print(f" - {record['id']} (Reason: {record['reason']})")

        # Exit with WARNING status
        sys.exit(1)
    else:
        print(f"Status Code: {response.status_code} \n")
        print(f"PASSED: All {len(results['pass'])} resources have published software within {max_age_days} days")

        print("\n The following items PASSED: \n")
        for record in results["pass"]:
            print(f" - {record['id']}")

        print("\n The following items were SKIPPED: \n")
        for record in results["skipped"]:
            print(f" - {record['id']} (Reason: {record['reason']})")

        sys.exit(0)  # Success

except Exception as e:
    print(f"UNKNOWN: Error checking API: {str(e)}")
    sys.exit(3)
