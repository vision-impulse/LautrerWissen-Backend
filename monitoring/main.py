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

import time
import signal
import sys
import time

from monitoring.access_analysis import run_goaccess
from monitoring.health_check import perform_health_check
from monitoring.config import DOCKER_CHECK_INTERVAL_SECONDS
from monitoring.config import LOG_ANALYSIS_INTERVAL_SECONDS
from monitoring.config import MAIN_LOOP_SLEEP_TIME
from monitoring.config import NGINX_OUTPUT_HTML
from monitoring.config import NGINX_LOG_PATH
from monitoring.config import SERVICE_CONFIG_FILE
from monitoring.config import DOCKER_OUTPUT_FILE
from monitoring.config import TCP_TIMEOUT_SECONDS
from monitoring.config import HEARTBEAT_MAX_DELAY_MINUTES


RUNNING = True

# --- Utility Functions ---
def signal_handler(sig: int, frame: object) -> None:
    """Handles OS signals (SIGINT, SIGTERM) for graceful exit."""
    global RUNNING
    print(f"\n[Monitor] Signal {sig} received. Preparing to shut down gracefully...")
    RUNNING = False


def setup_signal_handlers():
    """Sets up handlers for common termination signals."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# --- Main Logic ---
def main():
    """The main entry point for the monitoring script."""
    global RUNNING
    setup_signal_handlers()

    print(f"[Monitor] Starting monitoring loop at intervals:")
    print(
        f"[Monitor]   - Docker component checks: every {DOCKER_CHECK_INTERVAL_SECONDS} seconds"
    )
    print(f"[Monitor]   - Log analysis tasks: every {LOG_ANALYSIS_INTERVAL_SECONDS} seconds")

    # Initialize timers to ensure all tasks run immediately upon start
    current_time = time.time()
    last_docker_check_time = current_time - DOCKER_CHECK_INTERVAL_SECONDS
    last_log_analysis_time = current_time - LOG_ANALYSIS_INTERVAL_SECONDS

    try:
        while RUNNING:
            current_time = time.time()

            # 1. Docker Component Checks
            if (current_time - last_docker_check_time) >= DOCKER_CHECK_INTERVAL_SECONDS:
                print("-" * 40)
                """Performs TCP connection checks / heartbeats of critical Docker services."""
                perform_health_check(
                    SERVICE_CONFIG_FILE,
                    DOCKER_OUTPUT_FILE,
                    TCP_TIMEOUT_SECONDS,
                    HEARTBEAT_MAX_DELAY_MINUTES,
                )
                last_docker_check_time = current_time
                print("-" * 40)

            # 2. Log Analysis and Statistics
            if (current_time - last_log_analysis_time) >= LOG_ANALYSIS_INTERVAL_SECONDS:
                print("=" * 60)
                """Generates and stores access statistics for web services."""
                print(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] LOG ANALYSIS: Creating access statistics and metrics..."
                )
                run_goaccess(NGINX_LOG_PATH, NGINX_OUTPUT_HTML)
                last_log_analysis_time = current_time
                print("=" * 60)

            # Wait for the next check cycle
            if RUNNING:
                time.sleep(MAIN_LOOP_SLEEP_TIME)

    except Exception as e:
        print(f"[Monitor] An unexpected error occurred: {e}", file=sys.stderr)
        RUNNING = False
    finally:
        print("[Monitor] Monitoring script finished.")


if __name__ == "__main__":
    main()
