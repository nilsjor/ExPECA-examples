#!/usr/bin/env python3

import requests
import json
import sys
import os
import glob

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
# CONFIGURATION - Update these for your environment
# ------------------------------------------------------------------------------
GRAFANA_URL = "http://" + config["address"] + ":3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = config["grafana_psw"]

# Folder ID (integer). Use 0 to put in "General" folder, or specify another folder's ID.
# (You can list folders via Grafana API or UI if you want to place the dashboard
# in a custom folder.)
FOLDER_ID = 0

# Overwrite behavior: set to True if you want to overwrite an existing dashboard
# with the same UID/title.
OVERWRITE_EXISTING = False


def import_dashboards():
    """
    Looks for all JSON files matching 'dashboard*.json' in the current directory
    and imports them into Grafana (one by one).
    """

    # Find all JSON files matching the wildcard pattern
    dashboard_files = glob.glob("dashboard*.json")
    if not dashboard_files:
        print("No 'dashboard*.json' files found in the current directory.")
        sys.exit(1)

    # For each file, read and import the dashboard
    for dash_file in sorted(dashboard_files):
        print(f"\n=== Importing '{dash_file}' ===")

        # 1) Read and parse the JSON
        if not os.path.isfile(dash_file):
            print(f"Error: File not found: {dash_file}")
            continue

        try:
            with open(dash_file, "r", encoding="utf-8") as f:
                dashboard_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON from {dash_file}: {e}")
            continue

        # 2) Clean up the dashboard JSON (remove or reset ID, version, etc.)
        if "id" in dashboard_data and dashboard_data["id"] is not None:
            dashboard_data["id"] = None

        if "version" in dashboard_data:
            dashboard_data["version"] = 0

        # 3) Construct the payload for the Grafana API
        payload = {
            "dashboard": dashboard_data,
            "folderId": FOLDER_ID,
            "overwrite": OVERWRITE_EXISTING
        }

        # 4) Make the POST request to import the dashboard
        url = f"{GRAFANA_URL}/api/dashboards/db"
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                url,
                auth=(GRAFANA_USER, GRAFANA_PASS),
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            print(f"Dashboard '{dash_file}' imported successfully!")
            print("Server response:", response.json())
        except requests.exceptions.HTTPError as http_err:
            print("Failed to import dashboard.")
            print(f"HTTP status code: {response.status_code}")
            print("Response content:", response.text)
            print("Error:", http_err)
        except Exception as err:
            print("An unexpected error occurred:", str(err))

    print("\nAll matching dashboards processed.")


if __name__ == "__main__":
    import_dashboards()
