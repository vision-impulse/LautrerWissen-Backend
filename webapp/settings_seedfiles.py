#!/usr/bin/env python
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

APP_CONFIG_DIR = os.getenv("APP_CONFIG_DIR", "./config")
APP_DATA_DIR = os.getenv("APP_DATA_DIR", "./appdata")

SEED_FILES = {
    # Seed config files
    "sidebar_config": os.path.join(APP_CONFIG_DIR, "init/frontend_sidebar_config.json"),
    "data_sources_config": os.path.join(APP_CONFIG_DIR, "init/datasources_config.yaml"),
    
    # Seed data files
    "dashboard_data_file": os.path.join(APP_DATA_DIR, "init/dashboards.yaml"),
    "demographics_data_file": os.path.join(APP_DATA_DIR, "init/demographics.csv"),
    "election_data_file": os.path.join(APP_DATA_DIR, "init/bundestagswahl_2025.csv"),
    "fieldtest_sql_file": os.path.join(APP_DATA_DIR, "init/fieldtest_dump_hd.sql"),
}
