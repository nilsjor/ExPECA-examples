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
AUTH = (USERNAME, PASSWORD)

# Optional mapping: backup datasource name -> target datasource name.
DS_MAPPING_CONFIG = config.get("datasourceMapping", {})  
# Optional default datasource to use if no match is found.
DEFAULT_DS = config.get("defaultDatasource", "")

def load_backup_ds_mapping(input_file="datasources.json"):
    """
    Load the backup datasources and build a mapping from backup datasource UID to its name.
    """
    mapping = {}
    if not os.path.exists(input_file):
        print(f"Datasource backup file '{input_file}' not found.")
        return mapping
    with open(input_file, "r") as f:
         datasources = json.load(f)
    for ds in datasources:
         if "uid" in ds and "name" in ds:
             mapping[ds["uid"].strip()] = ds["name"].strip()
    return mapping

def fetch_target_datasources(base_url, auth):
    """
    Fetch datasources from the target Grafana instance and return a set of datasource names.
    """
    ds_url = f"{base_url}/api/datasources"
    response = requests.get(ds_url, auth=auth, verify=False)
    if response.status_code != 200:
        print(f"Error fetching target datasources: {response.text}")
        sys.exit(1)
    ds_list = response.json()
    ds_names = set()
    for ds in ds_list:
        if "name" in ds:
            ds_names.add(ds["name"].strip())
    return ds_names

def update_datasource_references_target(item, target_ds_names, backup_ds_mapping, mapping_config, default_ds):
    """
    Recursively update datasource references in the JSON object.

    For each "datasource" key holding an object:
      - If the object's UID is "-- Grafana --", leave it unchanged.
      - Otherwise, try to obtain a name:
          (1) Use the "name" field if present.
          (2) If missing, use the UID to look up the backup datasource name.
          (3) If still missing, fall back to using the "type" field.
      - Then, if that name is in the target datasources, use it.
      - Else, if mapping_config provides a mapping, use that.
      - Otherwise, use default_ds.
      
    If the "datasource" key holds a string (even empty), it is left unchanged.
    """
    if isinstance(item, dict):
        for key, value in item.items():
            if key == "datasource":
                if isinstance(value, dict):
                    # Special case: built-in Grafana datasource remains unchanged.
                    if value.get("uid", "").strip() == "-- Grafana --":
                        item[key] = "-- Grafana --"
                        continue
                    # Try to resolve a datasource name.
                    backup_ds_name = value.get("name", "").strip()
                    if not backup_ds_name and "uid" in value:
                        backup_ds_name = backup_ds_mapping.get(value["uid"].strip(), "").strip()
                    if not backup_ds_name and "type" in value:
                        backup_ds_name = value["type"].strip()
                    
                    if backup_ds_name in target_ds_names:
                        item[key] = backup_ds_name
                    elif backup_ds_name in mapping_config:
                        mapped = mapping_config[backup_ds_name].strip()
                        if mapped in target_ds_names:
                            item[key] = mapped
                        else:
                            print(f"Warning: Mapped target datasource '{mapped}' for backup '{backup_ds_name}' not found in target. Using default.")
                            item[key] = default_ds
                    else:
                        print(f"Warning: Datasource '{backup_ds_name}' not found in target and no mapping provided. Using default.")
                        item[key] = default_ds
                # Otherwise, if not a dict, leave as is.
            else:
                update_datasource_references_target(value, target_ds_names, backup_ds_mapping, mapping_config, default_ds)
    elif isinstance(item, list):
        for elem in item:
            update_datasource_references_target(elem, target_ds_names, backup_ds_mapping, mapping_config, default_ds)

def fix_panel_datasource(panel):
    """
    If the panel-level "datasource" is empty, and if there is at least one target
    with a valid (non-empty) datasource string, then update the panel-level datasource.
    """
    if "datasource" in panel and panel["datasource"] == "" and "targets" in panel:
        for target in panel["targets"]:
            ds = target.get("datasource")
            if isinstance(ds, str) and ds != "":
                panel["datasource"] = ds
                return
            elif isinstance(ds, dict):
                # In case the target's datasource is still an object, try to resolve it.
                name = ds.get("name", "").strip()
                if name:
                    panel["datasource"] = name
                    return

def restore_datasources(base_url, auth, input_file="datasources.json"):
    """Restore Grafana datasources from the backup file."""
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found. Cannot restore datasources.")
        sys.exit(1)
    with open(input_file, "r") as f:
        datasources = json.load(f)
    for ds in datasources:
        print(f"Restoring datasource: {ds.get('name', 'Unnamed')}...")
        resp = requests.post(f"{base_url}/api/datasources", auth=auth, json=ds, verify=False)
        if resp.status_code in [200, 201]:
            print(f"✔ Datasource '{ds.get('name')}' restored successfully!")
        else:
            print(f"⚠ Failed to restore datasource '{ds.get('name')}': {resp.text}")

def restore_dashboards(base_url, auth, backup_ds_mapping, target_ds_names, mapping_config, default_ds, input_file="dashboards.json"):
    """Restore Grafana dashboards from backup after updating datasource references."""
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found. Cannot restore dashboards.")
        sys.exit(1)
    with open(input_file, "r") as f:
        dashboards = json.load(f)
    for dashboard_data in dashboards:
        dashboard = dashboard_data.get("dashboard")
        if not dashboard:
            print("⚠ Skipping invalid dashboard JSON structure.")
            continue
        print(f"Restoring dashboard: {dashboard.get('title', 'Unknown Title')}...")
        # Update datasource references in the dashboard.
        update_datasource_references_target(dashboard, target_ds_names, backup_ds_mapping, mapping_config, default_ds)
        # Now fix panel-level datasource if empty by using the first target's datasource.
        if "panels" in dashboard and isinstance(dashboard["panels"], list):
            for panel in dashboard["panels"]:
                fix_panel_datasource(panel)
        # Remove internal id and uid so that Grafana assigns new ones.
        dashboard.pop("id", None)
        dashboard.pop("uid", None)
        dashboard["version"] = 0
        payload = {
            "dashboard": dashboard,
            "folderId": 0,       # Change if you wish to restore into a specific folder.
            "overwrite": False   # Set to True if you wish to overwrite dashboards with the same title.
        }
        resp = requests.post(f"{GRAFANA_URL}/api/dashboards/db", auth=auth, json=payload, verify=False)
        if resp.status_code in [200, 201]:
            print(f"✔ Dashboard '{dashboard.get('title')}' restored successfully!")
        else:
            print(f"⚠ Failed to restore dashboard '{dashboard.get('title')}': {resp.text}")

def main():
    # Build mapping from backup datasource UIDs to names.
    backup_ds_mapping = load_backup_ds_mapping("datasources.json")
    print("Backup datasource mapping:", backup_ds_mapping)
    # Fetch the target instance datasource names.
    target_ds_names = fetch_target_datasources(GRAFANA_URL, AUTH)
    print("Target instance datasources:", target_ds_names)
    # Restore datasources from backup.
    # restore_datasources(GRAFANA_URL, AUTH)
    # Restore dashboards, updating datasource references.
    restore_dashboards(GRAFANA_URL, AUTH, backup_ds_mapping, target_ds_names, DS_MAPPING_CONFIG, DEFAULT_DS)

if __name__ == "__main__":
    main()
