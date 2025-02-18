#!/usr/local/nagios/venv/bin/python3
import requests, json, sys
from datetime import datetime, timezone

url = "URL VALUE HERE"

try:
    resp = requests.get(url)
    record = json.loads(resp.text)['record_list'][0]

    end_time = datetime.strptime(record["ProcessingEnd"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    is_recent = (datetime.now(timezone.utc) - end_time).days < 1

    if is_recent and record["ProcessingCode"] == "0":
        print("PASSED: API response is recent and ProcessCode == 0")
        sys.exit(0)
    print("FAILED: API response is too old OR ProcessCode != 0")
    sys.exit(2)

except Exception as e:
    print(f"UNKNOWN: Error checking API: {str(e)}")
    sys.exit(3)
