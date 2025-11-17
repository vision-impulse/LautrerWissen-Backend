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

import os 

# Main intervalls for checks
MAIN_LOOP_SLEEP_TIME = int(os.getenv("MAIN_LOOP_SLEEP_TIME", "120"))  
DOCKER_CHECK_INTERVAL_SECONDS = int(os.getenv("DOCKER_CHECK_INTERVAL_SECONDS", "600"))  
LOG_ANALYSIS_INTERVAL_SECONDS = int(os.getenv("LOG_ANALYSIS_INTERVAL_SECONDS", "3600"))  

# Nginx log analysis
NGINX_LOG_PATH = "/logs/components/nginx/access.log"
NGINX_OUTPUT_HTML = "/logs/analysis/nginx_report.html"

# Docker component analysis
SERVICE_CONFIG_FILE = "/config/components/health-monitoring/services.json"
DOCKER_OUTPUT_FILE = "/logs/analysis/docker_status.json"
TCP_TIMEOUT_SECONDS = 1.0
HEARTBEAT_MAX_DELAY_MINUTES = DOCKER_CHECK_INTERVAL_SECONDS + MAIN_LOOP_SLEEP_TIME * 2



