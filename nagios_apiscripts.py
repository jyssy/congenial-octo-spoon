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

# Map base_names to actual Nagios hostnames
host_mapping = {
    "opsapi_beta": "operations-beta-api.access-ci.org",
    "opsapi_prod": "operations-api.access-ci.org"
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

# Template for command definition
COMMAND_TEMPLATE = """

# Ops_API_{base_name}_{endpoint_name}_Check
define command{{
        command_name    Ops_API_{base_name}_{endpoint_name}_Check
        command_line    /usr/local/nagios/venv/bin/python3 /usr/local/nagios/Ops_API_{base_name}_{endpoint_name}_Check.py
        }}

"""

# Template for service definition
SERVICE_TEMPLATE = """

define service{{
        use                             Critical-Service
        host_name                       {hostname}
        service_description             Ops_API_{base_name}_{endpoint_name}_Check
        check_command                   Ops_API_{base_name}_{endpoint_name}_Check
        check_interval                  60
        retry_interval                  5
        max_check_attempts              3
        notification_interval           1440
        notification_period             24x7
        notification_options            w,u,c
        contacts                        navarro, blau
#        notifications_enabled           0
}}

"""

# Create output directory
os.makedirs("nagios_checks", exist_ok=True)

# Initialize Nagios config files
with open("ops_api_command_defs.cfg", "w") as cmd_file:
    cmd_file.write("# Operations API Command Definitions for Nagios\n\n")

with open("ops_api_service_defs.cfg", "w") as svc_file:
    svc_file.write("# Operations API Service Definitions for Nagios\n\n")

# Initialize counters
command_count = 0
service_count = 0

# Generate scripts and config for each combination
for base_name, base_url in base_urls.items():
    # Get the corresponding hostname for this base_name
    hostname = host_mapping[base_name]

    for endpoint_name, endpoint_info in api_endpoints.items():
        # Format variables
        check_name = f"Ops_API_{base_name}_{endpoint_name}_Check"

        # 1. Generate Python check script
        script_content = TEMPLATE.format(
            base_name=base_name,
            endpoint_name=endpoint_name,
            base_url=base_url,
            api_path=endpoint_info,
            full_url=f"{base_url}{endpoint_info}"
        )

        # Create the script file
        filename = f"nagios_checks/{check_name}.py"
        with open(filename, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(filename, 0o755)

        # 2. Append command definition
        with open("ops_api_command_defs.cfg", "a") as cmd_file:
            cmd_file.write(COMMAND_TEMPLATE.format(
                base_name=base_name,
                endpoint_name=endpoint_name
            ))
        command_count += 1

        # 3. Append service definition
        with open("ops_api_service_defs.cfg", "a") as svc_file:
            svc_file.write(SERVICE_TEMPLATE.format(
                base_name=base_name,
                endpoint_name=endpoint_name,
                hostname=hostname  # Use the mapped hostname here
            ))
        service_count += 1

print(f"Generated {len(base_urls) * len(api_endpoints)} check scripts in 'nagios_checks'")
print(f"Generated {command_count} command definitions in 'ops_api_command_defs.cfg'")
print(f"Generated {service_count} service definitions in 'ops_api_service_defs.cfg'")
