# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

import json
import socket
import time
from datetime import datetime
import os


def perform_health_check(service_config_file, docker_output_file, tcp_timeout, heartbeat_max_delay_minutes):
    try:
        with open(service_config_file, 'r') as f:
            service_config = json.load(f)
            
        health_results = run_health_check(service_config, tcp_timeout, heartbeat_max_delay_minutes)
        save_results(health_results, docker_output_file)
        
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found at {service_config_file}. Cannot run checks.")
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON format in {service_config_file}. Cannot run checks.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def run_health_check(config, tcp_timeout_seconds, heartbeat_max_delay_minutes):
    """
    Runs health checks on all services defined in the configuration.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "status_checks": []
    }

    print(f"Starting health check at {results['timestamp']}...")
    
    for service in config["services"]:
        name = service.get("name", "Unknown Service")
        hostname = service.get("hostname")
        port = service.get("port")
        check_type = service.get("type")
        log_path = service.get("log_path", None)

        status = "DOWN"
        if check_type == "heartbeat":
            max_delay_minutes = service.get("max_delay_minutes", heartbeat_max_delay_minutes)
            heartbeat_logfile = service.get("path")
            is_healthy, detail = check_heartbeat_file(heartbeat_logfile, max_delay_minutes)
            status = "OK" if is_healthy else "DOWN"
        elif check_type == "tcp":
            if hostname and port:
                is_healthy, detail = check_tcp_connection(hostname, port, tcp_timeout_seconds)
                status = "OK" if is_healthy else "DOWN"
        else:
            status = "SKIPPED"
            detail = f"Missing hostname/port or check type is not 'tcp' or 'heartbeat' (Type: {check_type})"
            
        # Log and store the result
        print(f"  -> Service: {service}, Status: {status} ({detail})")

        data = {
            "service_name": name,
            "check_type": check_type,
            "status": status,
        }
        if log_path:
            data["log_file"] = log_path
        results["status_checks"].append(data)
    return results


def check_tcp_connection(hostname, port, tcp_timeout):
    """
    Attempts to establish a TCP connection to the given host and port.
    Returns True if successful, False otherwise.
    """
    try:
        s = socket.create_connection((hostname, port), timeout=tcp_timeout)
        s.close()
        return True, "REACHABLE"
    except socket.timeout:
        return False, f"TIMEOUT after {tcp_timeout}s"
    except socket.error as e:
        return False, f"CONNECTION ERROR: {e}"
    except Exception as e:
        return False, f"UNKNOWN ERROR: {e}"


def check_heartbeat_file(heartbeat_logfile, max_heartbeat_delay_in_min):
    now = time.time()
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DOCKER CHECK: Checking service heartbeat: {heartbeat_logfile}...")

    try:
        # Check if the file exists
        if not os.path.exists(heartbeat_logfile):
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT FAILED: File not found at {heartbeat_logfile}. Service assumed down.")
            return False, "NO HEARTBEAT"

        # Read the timestamp
        with open(heartbeat_logfile, 'r') as f:
            last_heartbeat_ts_str = f.read().strip()
            last_heartbeat_ts = float(last_heartbeat_ts_str)

    except FileNotFoundError:
        # Redundant check, but good practice
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT FAILED: File not found (Path Check Failed).")
        return False, "NO HEARTBEAT"
    except ValueError:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT ERROR: File content is not a valid timestamp.")
        return False, "NO HEARTBEAT"
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT ERROR: Could not read or process file: {e}")
        return False, "NO HEARTBEAT"

    delay = now - last_heartbeat_ts
    delay_min = round(delay / 60, 2)

    if delay <= max_heartbeat_delay_in_min * 60:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT OK: Last received {delay_min} minutes ago (Threshold: {max_heartbeat_delay_in_min} min).")
        return True, "HEARTBEAT"
    else:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEARTBEAT FAILED: Delay of {delay_min} minutes exceeds threshold ({max_heartbeat_delay_in_min} min).")
        return False, "NO HEARTBEAT"


def save_results(results, docker_output_file):
    """
    Saves the results dictionary to the specified JSON file path.
    Creates the directory if it doesn't exist.
    """
    try:
        # Ensure the output directory exists
        output_dir = os.path.dirname(docker_output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(docker_output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSuccessfully wrote health check results to {docker_output_file}")
        
    except Exception as e:
        # Print error to console so it's visible in docker logs
        print(f"\nCRITICAL ERROR: Could not write to output file {docker_output_file}. {e}")

