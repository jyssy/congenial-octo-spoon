import json
import os

# Load configs
with open('base_urls.json') as f:
    all_base_urls = json.load(f)

with open('api_endpoints.json') as f:
    api_endpoints = json.load(f)

# Filter to only use prod and beta base_urls
base_urls = {
    k: v for k, v in all_base_urls.items()
    if k in ["opsapi_beta", "opsapi_prod"]
}

# Template for Nagios check script
TEMPLATE = """#!/usr/local/nagios/venv/bin/python3
import sys
import json
import requests

# Nagios check for {endpoint_name} on {base_name}
base_url = "{base_url}"
api_path = "{api_path}"
full_url = base_url + api_path

try:
    response = requests.get(full_url, timeout=5)
    print(f"TESTING API: {full_url}")
    print(f"RESPONSE: {{response.status_code}}")

    if response.status_code == 200:
        print("PASSED: Successful response.")
        try:
            data = response.json()
            json_str = json.dumps(data, indent=2)
            print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            sys.exit(0)
        except json.JSONDecodeError:
            print("FAILED: Response is not valid JSON")
            sys.exit(2)
    else:
        print(f"FAILED: Got status code {{response.status_code}}")
        sys.exit(2)
except requests.RequestException as e:
    print(f"Error calling {full_url}: {{e}}")
    sys.exit(3)
"""

# Create output directory
os.makedirs("nagios_checks", exist_ok=True)

# script for each iteration
for base_name, base_url in base_urls.items():
    for endpoint_name, endpoint_info in api_endpoints.items():
        script_content = TEMPLATE.format(
            base_name=base_name,
            endpoint_name=endpoint_name,
            base_url=base_url,
            api_path=endpoint_info,
            full_url=f"{base_url}{endpoint_info}"
        )

        # Create the script file
        filename = f"nagios_checks/Nagios_{base_name}_{endpoint_name}_apiCheck.py"
        with open(filename, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(filename, 0o755)

print(f"Generated {len(base_urls) * len(api_endpoints)} check scripts in 'nagios_checks'")
