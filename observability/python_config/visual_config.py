#!/usr/bin/env python3

import subprocess
import sys
import os

# List your scripts in the order you want them to run:
scripts_to_run = [
    "influxdb_init.py",
    "grafana_init.py",
    "grafana_influxdb_datasource.py",
    "grafana_mqtt_datasource.py",
    "grafana_restore.py"
]

os.chdir(sys.path[0])            # Set current directory to script directory


def run_script(script_name):
    """
    Run a Python script in the same directory as this file.
    Raises an error if the script fails (non-zero exit).
    """
    script_path = script_name
    print(f"\n=== Running {script_path} ===")
    try:
        # Call with the same Python interpreter running this file
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {script_name} exited with return code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Error: Could not find script {script_name} at {script_path}")
        sys.exit(1)
    print(f"=== Completed {script_name} ===\n")


if __name__ == "__main__":
    for script in scripts_to_run:
        run_script(script)

    print("All scripts executed successfully!")
