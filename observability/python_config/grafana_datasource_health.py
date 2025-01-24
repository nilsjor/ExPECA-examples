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
# CONFIGURATION - Update these for your environment
# ------------------------------------------------------------------------------
GRAFANA_URL = "http://" + config["address"] + ":3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = config["grafana_psw"]

INFLUXDB_URL = "http://" + config["address"] + ":8086"  # InfluxDB 2.x base URL
INFLUXDB_ORG = config["influxdb_org"]
INFLUXDB_BUCKET = config["influxdb_bucket"]
INFLUXDB_TOKEN = config["influxdb_token"]              # All-access or read/write token

DATASOURCE_NAME = config["grafana_datasource"]

# ------------------------------------------------------------------------------
# STEP 1: CREATE OR UPDATE THE DATASOURCE
# ------------------------------------------------------------------------------
def create_influxdb_datasource():
    """
    Creates a new Grafana data source for InfluxDB 2.x (Flux).
    Returns the parsed JSON response from Grafana if successful.
    """
    datasource_payload = {
        "name": DATASOURCE_NAME,
        "type": "influxdb",
        "url": INFLUXDB_URL,
        "access": "proxy",
        "basicAuth": False,
        "jsonData": {
            "version": "Flux",
            "organization": INFLUXDB_ORG,
            "defaultBucket": INFLUXDB_BUCKET,
        },
        "secureJsonData": {
            "token": INFLUXDB_TOKEN
        }
    }

    headers = {
        "Content-Type": "application/json"
    }
    url = f"{GRAFANA_URL}/api/datasources"

    try:
        response = requests.post(
            url,
            auth=(GRAFANA_USER, GRAFANA_PASS),
            headers=headers,
            data=json.dumps(datasource_payload)
        )
        response.raise_for_status()
        print(f"Data source '{DATASOURCE_NAME}' created successfully.")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print("Failed to create data source.")
        print("Status Code:", response.status_code, "| Error:", err)
        print("Response content:", response.text)
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred while creating data source:", str(e))
        sys.exit(1)

# ------------------------------------------------------------------------------
# STEP 2: HEALTH CHECK (UNDOCUMENTED ENDPOINT)
# ------------------------------------------------------------------------------
def check_datasource_health(datasource_id):
    """
    Calls the undocumented 'health check' endpoint for the new data source,
    which mimics the 'Save & test' behavior in the Grafana UI.

    Endpoint: GET /api/datasources/proxy/{id}/health
    """
    url = f"{GRAFANA_URL}/api/datasources/proxy/{datasource_id}/health"
    print(f"Performing health check on data source ID {datasource_id}...")

    try:
        response = requests.get(
            url,
            auth=(GRAFANA_USER, GRAFANA_PASS)
        )
        # 200 typically indicates a successful connection; 
        # 401/403 might indicate auth problems, etc.
        if response.status_code == 200:
            print("Health check passed. Data source is working!")
            print("Health response:", response.text)
        else:
            print(f"Health check failed: {response.status_code}")
            print("Response content:", response.text)
    except requests.exceptions.RequestException as e:
        print("An error occurred while checking data source health:", str(e))

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # 1. Create the data source
    ds_response = create_influxdb_datasource()
    
    # 2. Parse out the ID from the creation response
    # Grafana's response may look like:
    # {
    #   "datasource": {
    #       "id": 4,
    #       "uid": "nErXDvDVk",
    #       "name": "influxdb-new",
    #       ...
    #   },
    #   "id": 4,
    #   "message": "Datasource added"
    # }
    #
    # We can first check "datasource.id", then fallback to "id".
    #
    datasource_id = None
    if "datasource" in ds_response and isinstance(ds_response["datasource"], dict):
        datasource_id = ds_response["datasource"].get("id")
    # Some Grafana versions might just return {"id": 4, ...} at top-level.
    if not datasource_id and "id" in ds_response:
        datasource_id = ds_response["id"]

    if not datasource_id:
        print("Warning: Could not find 'id' of new data source in Grafana response.")
        print("Response was:", ds_response)
        sys.exit(0)

    print(f"Got data source ID: {datasource_id}")

    # 3. Perform a health check on the newly created data source
    check_datasource_health(datasource_id)
