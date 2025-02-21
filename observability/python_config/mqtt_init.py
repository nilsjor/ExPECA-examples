#!/usr/bin/env python3
import json
import sys
import os
import time
import paho.mqtt.client as mqtt

# Ensure we run in the script's own directory:
os.chdir(sys.path[0])
configfname = "config_data.json"

try:
    with open(configfname, 'r') as f:
        config = json.load(f)
except Exception as e:
    print("Cannot read config data file:", e)
    sys.exit(1)

# MQTT Broker settings from config:
BROKER_ADDRESS = config["address"]
BROKER_PORT = 1883  # Default MQTT port

# Current admin credentials for the MQTT broker (assumed defaults)
ADMIN_USER = "default"
OLD_ADMIN_PASS = "defaultdefault"  # The old admin password

# Desired new password (provided in config as "mqtt_psw")
NEW_ADMIN_PASS = config["mqtt_psw"]

# Global variables to capture the broker's response and subscription confirmation
last_response = None
subscription_confirmed = False

def on_message(client, userdata, msg):
    """Callback to handle incoming messages on the control response topics."""
    global last_response
    try:
        payload = json.loads(msg.payload.decode())
    except Exception as e:
        print("Error decoding message payload:", e)
        return
    print(f"Received response on topic '{msg.topic}': {payload}")
    last_response = payload

def on_subscribe(client, userdata, mid, granted_qos):
    """Callback triggered when the subscription is confirmed by the broker."""
    global subscription_confirmed
    print("Subscription confirmed.")
    subscription_confirmed = True

def change_admin_password(client):
    """
    Changes the password for user "default" via the MQTT broker's dynamic security control command.
    
    The command is published to:
      $CONTROL/dynamic-security/v1/changePassword
    with a JSON payload containing:
      {
         "username": "default",
         "password": "<NEW_ADMIN_PASS>"
      }
    """
    global last_response
    topic = "$CONTROL/dynamic-security/v1/changePassword"
    payload = {
        "username": ADMIN_USER,
        "password": NEW_ADMIN_PASS
    }

    print(f"Changing password for MQTT admin user '{ADMIN_USER}' ...")
    client.publish(topic, json.dumps(payload))

    # Wait up to 10 seconds for a response
    timeout = 20
    start_time = time.time()
    while last_response is None and (time.time() - start_time) < timeout:
        time.sleep(0.1)
    if last_response is None:
        print("Timeout waiting for response from the broker.")
        sys.exit(1)
    if last_response.get("result") == "success":
        print("Password changed successfully!")
    else:
        print("Failed to change password. Response:", last_response)
        sys.exit(1)

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Create and configure the MQTT client
    client = mqtt.Client(client_id="mqtt_change_admin_password")
    client.username_pw_set(ADMIN_USER, OLD_ADMIN_PASS)
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
    except Exception as e:
        print("Failed to connect to MQTT broker:", e)
        sys.exit(1)

    # Subscribe to the dynamic security control response topics
    client.subscribe("$CONTROL/dynamic-security/v1/response/#")

    client.loop_start()  # Start the network loop in a background thread

    # Wait until the subscription is confirmed before sending the command.
    subscription_timeout = 5  # seconds
    start_time = time.time()
    while not subscription_confirmed and (time.time() - start_time) < subscription_timeout:
        time.sleep(0.1)

    if not subscription_confirmed:
        print("Failed to confirm subscription within timeout.")
        client.loop_stop()
        client.disconnect()
        sys.exit(1)

    # Change the admin password
    change_admin_password(client)

    client.loop_stop()
    client.disconnect()

    print(f"\nDone! The MQTT admin user's password has been updated to:")
    print(f"  username: {ADMIN_USER}")
    print(f"  password: {NEW_ADMIN_PASS}")
