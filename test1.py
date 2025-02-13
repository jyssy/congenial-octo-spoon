import requests
import json
from datetime import datetime, timezone

def run_api_test():
    BASE_URL = "URL WITH OUTPUT AS JSON HERE"

    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Content: {response.text}")

    data = json.loads(response.text)
    record = data['record_list'][0]

    processing_end = datetime.strptime(record["ProcessingEnd"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    time_diff = current_time - processing_end
    is_recent = time_diff.days < 1

    conditions = {
        "Recent Execution": is_recent,
        "Processing Code": record["ProcessingCode"] == "0"
    }

    all_passed = all(conditions.values())
    print(f"Test {'PASSED' if all_passed else 'FAILED: Response older than 1 day or ProcessCode != 0'}")

if __name__ == "__main__":
    run_api_test()
