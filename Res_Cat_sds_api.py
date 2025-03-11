#!/usr/local/nagios/venv/bin/python3
import requests, json, sys, random, os
from datetime import datetime, timezone

# PATH TO KEY
script_dir = os.path.dirname(os.path.abspath(__file__))
api_key_path = os.path.join(script_dir, "SDS_api_key")

# Ensure the file exists before reading
if not os.path.exists(api_key_path):
    print(f"UNKNOWN: API key file not found at {api_key_path}")
    sys.exit(3)

# Read the API key
try:
    with open(api_key_path, "r") as f:
        apiKey = f.read().strip()
except Exception as e:
    print(f"UNKNOWN: Error reading API key file: {str(e)}")
    sys.exit(3)

# https://ara-db.ccs.uky.edu/api=API_0/{apiKey}/rp={infoGroupId}?include=software_name,software_description,software_web_page,software_documentation,software_use_link

infoGroup_ids = [" ", " ", " "]
infoGroup_id = random.choice(infoGroup_ids)

url = f" URL "
headers = {"Origin": " URL "}
expected_keys =  ["software_name", "software_description", "software_web_page", "software_documentation"]

try:
    resp = requests.get(url, headers=headers)

    # Check HTTP status code
    if resp.status_code != 200:
        print(f"FAILED: HTTP status code: {resp.status_code} (expected 200)")
        sys.exit(2)

    # Check CORS headers
    cors_header = resp.headers.get('Access-Control-Allow-Origin')
    if not cors_header or (cors_header != "*" and cors_header != " URL from url "):
        print(f"FAILED: Missing or incorrect CORS header: {cors_header}")
        sys.exit(2)

    # Parse JSON response
    data = json.loads(resp.text)

    if not isinstance(data, list):
        print("FAILED: Response is not an array")
        sys.exit(2)

    if len(data) == 0:
        print("FAILED: Response array is empty")
        sys.exit(2)

    # Check for expected keys
    event = random.choice(data)
    missing_keys = [key for key in expected_keys if key not in event]
    if missing_keys:
        print(f"FAILED: Response missing expected keys: {', '.join(missing_keys)}")
        sys.exit(2)

    # All checks passed
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"PASSED: API response for group id: {infoGroup_id} at {current_time} has status code: {resp.status_code}, CORS headers: {cors_header}, with such array items as: {expected_keys}, etc..")
    sys.exit(0)

except Exception as e:
    print(f"UNKNOWN: Error checking API: {str(e)}")
    sys.exit(3)
