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

# -------------------------------
# Configuration Variables
# -------------------------------
INFLUXDB_HOST = config["address"]  # Host where InfluxDB is running
INFLUXDB_PORT = 8086             # Port for InfluxDB
USERNAME = "admin"               # Desired admin username
PASSWORD = config["influxdb_psw"]      # Desired password (even if auth is off, the setup endpoint requires it)
ORG_NAME = config["influxdb_org"]             # Desired organization name
BUCKET_NAME = config["influxdb_bucket"]          # Desired bucket name
RETENTION_DAYS = config["influxdb_retention_days"]              # Retention in days (e.g., 14d). Convert to seconds.

# Choose a specific token instead of letting InfluxDB generate one
CUSTOM_TOKEN = config["influxdb_token"]


def setup_influxdb_noauth():
    """
    Perform initial setup via the /api/v2/setup endpoint, and specify a custom token.
    Even if auth is disabled, you must supply username/password/bucket/org in the payload.
    """

    setup_url = f"http://{INFLUXDB_HOST}:{INFLUXDB_PORT}/api/v2/setup"

    # Convert days to seconds 
    retention_seconds = RETENTION_DAYS * 24 * 60 * 60

    # Prepare JSON data for the setup endpoint, including a custom token
    payload = {
        "username": USERNAME,
        "password": PASSWORD,  # Required by /api/v2/setup even if auth is disabled
        "org": ORG_NAME,
        "bucket": BUCKET_NAME,
        "retentionPeriodSeconds": retention_seconds,
        "token": CUSTOM_TOKEN  # <--- Use our desired token
    }

    try:
        response = requests.post(setup_url, json=payload)
        if response.status_code == 201:
            data = response.json()
            print("InfluxDB setup completed successfully!")
            print(f"User: {USERNAME}")
            print(f"Organization: {ORG_NAME}")
            print(f"Bucket: {BUCKET_NAME}")
            print(f"Retention: {RETENTION_DAYS}d")
            print(f"Custom Token Specified: {CUSTOM_TOKEN}")
            print("InfluxDB returned the following token in the response:")
            print(f"  {data['auth']['token']}")
            if data['auth']['token'] != CUSTOM_TOKEN:
                print("Note: The returned token may differ if InfluxDB overrides it,")
                print("but typically it will match your specified CUSTOM_TOKEN.")
        else:
            print(f"Setup failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to InfluxDB at {setup_url}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # pip install requests if needed
    setup_influxdb_noauth()
