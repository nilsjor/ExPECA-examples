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
except Exception as e:
    print("Cannot read config data file:", e)
    sys.exit(1)

# Configure Grafana URL and credentials from config
GRAFANA_URL = "http://" + config["address"] + ":3000"
USERNAME = "admin"
PASSWORD = config["grafana_psw"]

def update_datasource_references(dashboard):
    """
    Recursively updates datasource references in the dashboard JSON.
    If a panel's datasource is an object, replace it with its 'name' string.
    """
    def update_panel(panel):
        if isinstance(panel, dict):
            if "datasource" in panel:
                ds = panel["datasource"]
                if isinstance(ds, dict):
                    # Replace with the datasource name (or empty string if not found)
                    panel["datasource"] = ds.get("name", "")
                # If it's already a string, leave it unchanged.
            # Update nested panels if present.
            if "panels" in panel and isinstance(panel["panels"], list):
                for subpanel in panel["panels"]:
                    update_panel(subpanel)
    # For new dashboard format (top-level panels)
    if "panels" in dashboard and isinstance(dashboard["panels"], list):
        for panel in dashboard["panels"]:
            update_panel(panel)
    # For older dashboard format using rows.
    if "rows" in dashboard and isinstance(dashboard["rows"], list):
        for row in dashboard["rows"]:
            if "panels" in row and isinstance(row["panels"], list):
                for panel in row["panels"]:
                    update_panel(panel)
    return dashboard

def fetch_datasources(base_url, auth, output_file="datasources.json"):
    """Backup Grafana datasources."""
    datasources_url = f"{base_url}/api/datasources"
    print("Fetching datasources...")
    response = requests.get(datasources_url, auth=auth, verify=False)
    if response.status_code != 200:
        print(f"Error fetching datasources (status {response.status_code}): {response.text}")
        sys.exit(1)
    datasources = response.json()
    # Remove any existing "id" field to avoid conflicts on restore.
    for ds in datasources:
        ds.pop("id", None)
    with open(output_file, "w") as ds_file:
        json.dump(datasources, ds_file, indent=2)
    print(f"✔ Saved {len(datasources)} datasources to '{output_file}'.")

def fetch_dashboards(base_url, auth, output_file="dashboards.json"):
    """Backup Grafana dashboards."""
    search_url = f"{base_url}/api/search?query=&type=dash-db"
    print("Fetching dashboard list...")
    response = requests.get(search_url, auth=auth, verify=False)
    if response.status_code != 200:
        print(f"Error fetching dashboard list (status {response.status_code}): {response.text}")
        sys.exit(1)
    # Extract dashboard UIDs from the search results.
    dashboard_uids = [item['uid'] for item in response.json() if 'uid' in item]
    print(f"Found {len(dashboard_uids)} dashboards.")
    dashboards = []
    for uid in dashboard_uids:
        dashboard_url = f"{base_url}/api/dashboards/uid/{uid}"
        resp = requests.get(dashboard_url, auth=auth, verify=False)
        if resp.status_code == 200:
            dashboard_json = resp.json()
            # Update datasource references so that only the datasource name is used.
            if "dashboard" in dashboard_json:
                dashboard_json["dashboard"] = update_datasource_references(dashboard_json["dashboard"])
            dashboards.append(dashboard_json)
        else:
            print(f"⚠ Warning: Could not fetch dashboard {uid} (status {resp.status_code}). Skipping.")
    with open(output_file, "w") as db_file:
        json.dump(dashboards, db_file, indent=2)
    print(f"✔ Saved {len(dashboards)} dashboards to '{output_file}'.")

def main():
    auth = (USERNAME, PASSWORD)
    fetch_datasources(GRAFANA_URL, auth)
    fetch_dashboards(GRAFANA_URL, auth)

if __name__ == "__main__":
    main()
