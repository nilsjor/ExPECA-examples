#!/usr/bin/env python3
import requests
import json
import sys
import os

# Ensure we run in the script's own directory:
os.chdir(sys.path[0])
configfname = "config_data.json"

try:
    with open(configfname, 'r') as f:
        config = json.load(f)
except:
    print("Cannot read config data file")  
    sys.exit(1)  

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
GRAFANA_URL = "http://" + config["address"] + ":3000"

# Current admin credentials
ADMIN_USER = "admin"
OLD_ADMIN_PASS = "admin"             # The old admin password

# Desired new password
NEW_ADMIN_PASS = config["grafana_psw"]

# ------------------------------------------------------------------------------
# CHANGE ADMIN'S OWN PASSWORD
# ------------------------------------------------------------------------------
def change_own_admin_password():
    """
    Changes the currently authenticated user's password via:
    PUT /api/user/password
    
    The request body must contain:
      {
        "oldPassword": "<old_pass>",
        "newPassword": "<new_pass>"
      }
    """
    url = f"{GRAFANA_URL}/api/user/password"

    payload = {
        "oldPassword": OLD_ADMIN_PASS,
        "newPassword": NEW_ADMIN_PASS
    }

    print(f"Changing password for user '{ADMIN_USER}' (yourself) ...")
    resp = requests.put(url, auth=(ADMIN_USER, OLD_ADMIN_PASS), json=payload)

    if resp.status_code == 200:
        print("Password changed successfully!")
    else:
        print(f"Failed to change password. Status code: {resp.status_code}")
        print("Response:", resp.text)
        sys.exit(1)

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Attempt to change the admin's own password
    change_own_admin_password()

    print(f"\nDone! You can now log in as user '{ADMIN_USER}' with the new password:")
    print(f"  username: {ADMIN_USER}")
    print(f"  password: {NEW_ADMIN_PASS}")
