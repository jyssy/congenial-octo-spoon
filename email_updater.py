#!/usr/bin/python
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

def get_exact_email(username):
    try:
        resp = requests.get(base_url, params={'q': username.strip()}, headers=headers)
        if resp.status_code == 200:
            for result in resp.json().get('result', []):
                if result.get('portal_login') == username.strip():
                    return result.get('email', '').strip()
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
                          if len(line.strip().split(None, 1)) == 2 and line.strip().split()[0] in ['contact_name', 'email'])

            if 'contact_name' not in contact:
                continue

            username = contact['contact_name'].strip()
            local_email = contact.get('email', 'NOT_SET').strip()
            api_email = get_exact_email(username)

            if api_email and local_email != api_email:
                log_message(f"MISMATCH - {username}: '{local_email}' → '{api_email}'", new_log_content)
                if update_files and update_contact_email(cfg_file, username, local_email, api_email):
                    log_message(f"UPDATED - {username} in {cfg_file.name}", new_log_content)
            elif api_email:
                log_message(f"OK - {username}: '{local_email}'", new_log_content)
            else:
                log_message(f"NO_MATCH - {username}: No exact match found", new_log_content)

            time.sleep(0.3)

    log_message("=== Contact Email Check Completed ===", new_log_content)
    log_file.write_text("\n".join(new_log_content) + "\n" + existing_content)
    print(f"Results logged to: contact_changes.log")

except Exception as e:
    print(f"UNKNOWN: Error processing files: {str(e)}")
    sys.exit(3)
