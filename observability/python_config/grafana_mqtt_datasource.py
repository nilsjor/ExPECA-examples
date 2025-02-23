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

# Grafana connection settings using the provided address and Grafana password from config.
GRAFANA_URL  = "http://" + config["address"] + ":3000"
GRAFANA_USER = "admin"
GRAFANA_PASS = config["grafana_psw"]

# MQTT datasource settings.
# We assume the MQTT broker is on the same host (address) using the ws MQTT port 9001.
MQTT_URL       = "ws://" + config["address"] + ":9001"
MQTT_CLIENT_ID = "grafana-mqtt-client"
MQTT_TOPIC     = "#"  # Subscribe to all topics by default.
MQTT_QOS       = 0

# Datasource name as provided in the configuration file.
DATASOURCE_NAME = config["mqtt_datasource"]

# ------------------------------------------------------------------------------
# STEP 1: CREATE OR UPDATE THE MQTT DATASOURCE
# ------------------------------------------------------------------------------
def create_mqtt_datasource():
    """
    Creates a new Grafana datasource for MQTT using the grafana-mqtt-datasource plugin.
    Returns the parsed JSON response from Grafana if successful.
    """
    # print(MQTT_URL, type(MQTT_URL))
    # print(config["mqtt_psw"], type(config["mqtt_psw"]))
    # exit()

    datasource_payload = {
        "name": DATASOURCE_NAME,
        "type": "grafana-mqtt-datasource",  # This must match the plugin's type ID.
        "access": "proxy",                 # Let Grafana route the connection via its backend.
        "basicAuth": False,
        "isDefault": False,  # Ensure this datasource is not set as default
        "jsonData": {
            "Uri": MQTT_URL,
            "clientId": MQTT_CLIENT_ID,
            "topic": MQTT_TOPIC,
            "qos": MQTT_QOS,
            "username": config["mqtt_user"]         # Visible username.
        },
        "secureJsonData": {
            "password": config["mqtt_psw"] # The MQTT connection password stored securely.
        },
    }


    headers = {"Content-Type": "application/json"}
    url = f"{GRAFANA_URL}/api/datasources"

    try:
        response = requests.post(url,
                                 auth=(GRAFANA_USER, GRAFANA_PASS),
                                 headers=headers,
                                 data=json.dumps(datasource_payload))
        response.raise_for_status()
        print(f"Datasource '{DATASOURCE_NAME}' created successfully.")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print("Failed to create datasource.")
        print("Status Code:", response.status_code, "| Error:", err)
        print("Response content:", response.text)
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred while creating datasource:", e)
        sys.exit(1)

# ------------------------------------------------------------------------------
# STEP 2: HEALTH CHECK (UNDOCUMENTED ENDPOINT)
# ------------------------------------------------------------------------------
def check_datasource_health(datasource_id):
    """
    Calls the undocumented 'health check' endpoint for the new datasource,
    which mimics the 'Save & test' behavior in the Grafana UI.
    Endpoint: GET /api/datasources/proxy/{id}/health
    """
    url = f"{GRAFANA_URL}/api/datasources/proxy/{datasource_id}/health"
    print(f"Performing health check on datasource ID {datasource_id}...")

    try:
        response = requests.get(url, auth=(GRAFANA_USER, GRAFANA_PASS))
        if response.status_code == 200:
            print("Health check passed. Datasource is working!")
            print("Health response:", response.text)
        else:
            print(f"Health check failed: {response.status_code}")
            print("Response content:", response.text)
    except Exception as e:
        print("An error occurred while checking datasource health:", e)

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # 1. Create the MQTT datasource
    ds_response = create_mqtt_datasource()
    
    # 2. Parse out the ID from the creation response.
    # Grafana's response may have the datasource's ID in "datasource.id" or at the top level as "id".
    datasource_id = None
    if "datasource" in ds_response and isinstance(ds_response["datasource"], dict):
        datasource_id = ds_response["datasource"].get("id")
    if not datasource_id and "id" in ds_response:
        datasource_id = ds_response["id"]

    if not datasource_id:
        print("Warning: Could not find 'id' of new datasource in Grafana response.")
        print("Response was:", ds_response)
        sys.exit(0)

    print(f"Got datasource ID: {datasource_id}")

    # 3. Perform a health check on the newly created datasource
    # check_datasource_health(datasource_id)
