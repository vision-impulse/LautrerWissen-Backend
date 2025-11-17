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
import time
import subprocess
from datetime import datetime


def run_goaccess(log_path, output_html):
    if not os.path.exists(log_path):
        print(f"[WARN] Log file not found: {log_path}")
        return

    print(f"[{datetime.now()}] Running GoAccess analysis...")
    try:
        subprocess.run([
            "goaccess", log_path,
            "--log-format=COMBINED",
            "--ignore-crawlers",
            "--html-report-title=Lautrer Wissen - NGINX Access Statistics",
            "--output", output_html,
            "--json-pretty-print",
            "--keep-last", "10000",
        ], check=True)
        print(f"[{datetime.now()}] GoAccess report generated at {output_html}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] GoAccess failed: {e}")