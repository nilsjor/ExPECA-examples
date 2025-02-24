# Observability & Monitoring for Experimentation on the ExPECA Testbed

## Overview

This repository provides a **Docker-based visualization and monitoring solution** for the ExPECA testbed. It includes a **database, message broker, and visualization tools** to streamline experimentation and data analysis.

## Docker Image

A pre-configured Docker image is available, incorporating the following key components:

- **InfluxDB** – A time-series database supporting both user-provided and system-generated timestamps.
- **Eclipse Mosquitto** – An MQTT broker for streaming time-series data.
- **Grafana** – A powerful visualization tool for monitoring and analyzing data.

### Docker Image Details

- **Repository**: Docker Hub - `sman4ever/visual:latest`
- The container starts with a **basic initial configuration** for all included services:
  - **InfluxDB**: No initial authentication (must be set up manually).
  - **MQTT**: User credentials are defined via environment variables.
  - **Grafana**: Default admin credentials (`admin/admin`).

### Environment Variables

To deploy the container with the necessary configurations, define the following environment variables:

| Variable     | Description                             |
| ------------ | --------------------------------------- |
| `DNS_IP`     | DNS server IP address (e.g., `8.8.8.8`) |
| `GATEWAY_IP` | Gateway IP for internet access          |
| `PASS`       | Root SSH password                       |
| `MQTT_USER`  | Username for the MQTT broker            |
| `MQTT_PASS`  | Password for the MQTT broker            |

#### Example Configuration (ExPECA Testbed)

```json
{
  "DNS_IP": "8.8.8.8",
  "GATEWAY_IP": "130.237.11.97",
  "PASS": "defaultdefault",
  "MQTT_USER": "admin",
  "MQTT_PASS": "defaultdefault"
}
```

### Initial Configuration

After launching the container, **manual setup is required** for:

- **InfluxDB** – Create login credentials and an API token.
- **Grafana** – Configure the admin credentials.

To automate this process, **Python scripts are available** (see the Python Scripts section).

---

## Python Notebooks

To simplify setup and deployment on the **ExPECA testbed**, we provide two Python notebooks:

- `visual_public.ipynb` – Uses only a public IP connection.
- `visual_public_edge.ipynb` – Supports both public IP and an internal "edge-net" connection for intra-testbed communication.

These notebooks:

- Reserve a **worker node** and deploy the **visualization container**.
- If the **edge version** is used, the container is connected to an **internal network** for inter-container communication.

---

## Python Scripts

For ease of setup, a set of **automation scripts** is provided. These scripts:

- Configure **InfluxDB** and **Grafana** with login credentials and API tokens.
- Automatically create **Grafana data sources** for InfluxDB and MQTT.
- Provide **backup and restore functionality** for Grafana dashboards.

### Available Scripts

| Script                           | Function                                                                                 |
| -------------------------------- | ---------------------------------------------------------------------------------------- |
| `influxdb_init.py`               | Initializes InfluxDB (admin credentials, organization, bucket, retention, and API token) |
| `grafana_init.py`                | Configures the Grafana admin password                                                    |
| `grafana_influxdb_datasource.py` | Creates a Grafana data source for InfluxDB                                               |
| `grafana_mqtt_datasource.py`     | Creates a Grafana data source for the MQTT broker                                        |
| `grafana_backup.py`              | Backs up existing Grafana dashboards to `dashboards.json`                                |
| `grafana_restore.py`             | Restores Grafana dashboards from `dashboards.json`                                       |
| `visual_config.py`               | Runs a sequence of selected scripts for quick setup                                      |

#### Example Automation Sequence

You can execute a predefined sequence of setup scripts using `visual_config.py`:

```python
scripts_to_run = [
    "influxdb_init.py",
    "grafana_init.py",
    "grafana_influxdb_datasource.py",
    "grafana_mqtt_datasource.py",
    "grafana_restore.py"
]
```

With these scripts, a **new visualization container can be fully set up within seconds**, ensuring repeatable and efficient deployments.

---

## Configuration File

A JSON configuration file (`config_data.json`) is used by the Python scripts and contains necessary credentials and parameters. Store this
file in the same directory as the Python scripts.

```json
{
    "address": "x.x.x.x",
    "grafana_psw": "defaultdefault",
    "influxdb_psw": "defaultdefault",
    "influxdb_org": "default",
    "influxdb_bucket": "default",
    "influxdb_retention_days": 14,
    "influxdb_token": "default",
    "influxdb_datasource": "influxdb",
    "mqtt_user": "admin"
    "mqtt_psw": "defaultdefault"
    "mqtt_datasource": "mqtt"
}
```

- The `address` field should be set to the **public IP** of the container.
- The `mqtt_user/mqtt_psw` fields need to be the same as what was used for the `MQTT_USER/MQTT_PASS` container environmental variables earlier
- Ensure the **InfluxDB password** is at least **8 characters long**.
- Modify other parameters to suit your setup.

---

## Typical Setup Procedure

The typical procedure for a quick, secure, and repeatable setup of the visualization system is as follows:

1. Run `visual_public.ipynb` or `visual_public.ipynb` with the desired parameters
2. Make sure that the appropriate parameter values are set in the `config_data.json` file
3. Run `visual_config.py` script, which in turn runs a configured sequence of setup scripts

Voila! Your visualization system is up and running, all within a few minutes. You now have your own secure credentials and your favorite
Grafana dashboards ready to show off your latest experimentation.

## Conclusion

This project provides a **fully automated, Docker-based monitoring solution** for ExPECA. By leveraging **Python scripts and Python notebooks**, users can quickly deploy, configure, and manage the visualization environment.

For further details, refer to the provided scripts and notebooks.

