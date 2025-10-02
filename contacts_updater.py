#!/usr/bin/python
# this script used CoPilot to be written
import requests, re, os, time, sys
from pathlib import Path
from datetime import datetime

# Read API key
try:
    API_KEY = os.environ.get('API_KEY') or Path('/users/jelambeadmin/soft/access_django_user_admin/API_KEY').read_text().strip()
except Exception as e:
    print(f"UNKNOWN: Error reading API key: {str(e)}")
    sys.exit(3)

# Configuration
base_url = "https://allocations-api.access-ci.org/acdb/userinfo/v2/people/search"
headers = {"XA-RESOURCE": "operations.django", "XA-AGENT": "userinfo", "XA-API-KEY": API_KEY}
update_files = '--update' in sys.argv

def log_message(message, log_content):
    log_content.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def get_user_info(username):
    try:
        resp = requests.get(base_url, params={'q': username.strip()}, headers=headers)
        if resp.status_code == 200:
            for result in resp.json().get('result', []):
                if result.get('portal_login') == username.strip():
                    email = result.get('email', '').strip()
                    first_name = result.get('first_name', '').strip()
                    last_name = result.get('last_name', '').strip()
                    full_name = f"{first_name} {last_name}".strip()
                    return {'email': email, 'full_name': full_name}
    except Exception:
        pass
    return None

def update_contact_email(cfg_file, username, old_email, new_email):
    content = cfg_file.read_text()
    pattern = rf'(define contact\s*\{{[^}}]*contact_name\s+{re.escape(username)}[^}}]*email\s+){re.escape(old_email)}'
    updated = re.sub(pattern, rf'\1{new_email}', content, flags=re.DOTALL)
    if updated != content:
        cfg_file.write_text(updated)
        return True
    return False

def update_contact_alias(cfg_file, username, old_alias, new_alias):
    content = cfg_file.read_text()
    pattern = rf'(define contact\s*\{{[^}}]*contact_name\s+{re.escape(username)}[^}}]*alias\s+){re.escape(old_alias)}'
    updated = re.sub(pattern, rf'\1{new_alias}', content, flags=re.DOTALL)
    if updated != content:
        cfg_file.write_text(updated)
        return True
    return False

# Main execution
log_file = Path('contact_changes.log')
existing_content = log_file.read_text() if log_file.exists() else ""
new_log_content = []
log_message("=== Contact Email Check Started ===", new_log_content)

try:
    for cfg_file in Path('.').glob("*.cfg"):
        log_message(f"Processing: {cfg_file.name}", new_log_content)

        for block in re.findall(r'define contact\s*\{(.*?)\}', cfg_file.read_text(), re.DOTALL):
            contact = dict(line.strip().split(None, 1) for line in block.strip().split('\n')
                          if len(line.strip().split(None, 1)) == 2 and line.strip().split()[0] in ['contact_name', 'email', 'alias'])

            if 'contact_name' not in contact:
                continue

            username = contact['contact_name'].strip()
            local_email = contact.get('email', 'NOT_SET').strip()
            local_alias = contact.get('alias', 'NOT_SET').strip()

            user_info = get_user_info(username)

            if user_info:
                api_email = user_info['email']
                api_full_name = user_info['full_name']

                # Check and update email
                if api_email and local_email != api_email:
                    log_message(f"EMAIL MISMATCH - {username}: '{local_email}' → '{api_email}'", new_log_content)
                    if update_files and update_contact_email(cfg_file, username, local_email, api_email):
                        log_message(f"EMAIL UPDATED - {username} in {cfg_file.name}", new_log_content)
                elif api_email:
                    log_message(f"EMAIL OK - {username}: '{local_email}'", new_log_content)

                # Check and update alias/name
                if api_full_name and local_alias != api_full_name:
                    log_message(f"NAME MISMATCH - {username}: '{local_alias}' → '{api_full_name}'", new_log_content)
                    if update_files and update_contact_alias(cfg_file, username, local_alias, api_full_name):
                        log_message(f"NAME UPDATED - {username} in {cfg_file.name}", new_log_content)
                elif api_full_name:
                    log_message(f"NAME OK - {username}: '{local_alias}'", new_log_content)
            else:
                log_message(f"NO_MATCH - {username}: No exact match found", new_log_content)

            time.sleep(0.3)

    log_message("=== Contact Email Check Completed ===", new_log_content)
    log_file.write_text("\n".join(new_log_content) + "\n" + existing_content)
    print(f"Results logged to: contact_changes.log")

except Exception as e:
    print(f"UNKNOWN: Error processing files: {str(e)}")
    sys.exit(3)
