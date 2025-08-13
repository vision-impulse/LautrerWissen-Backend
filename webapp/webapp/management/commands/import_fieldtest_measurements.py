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
 
import csv
import re
import json
import logging

from django.core.management.base import BaseCommand
from lautrer_wissen.models.geo.kl import KLFieldtestMeasurements
import csv
import os
from datetime import datetime
from django.db.models import Q

logger = logging.getLogger("django")


# Output columns (add 'deveui' as requested)
columns = [
    "time", "payloadHex", "battery", "latitude", "longitude", "sats",
    "triggered", "rssi", "snr", "uplink", "downlink", "deveui", "invalid", "rawdata"
]

# Regex pattern to extract values from the INSERT statement
insert_pattern = re.compile(r"INSERT INTO.*?VALUES\s*(.+);", re.DOTALL)
row_pattern = re.compile(r"\((.*?)\),?", re.DOTALL)

def parse_row(row_str):
    """Parses a single SQL value row into Python data types."""
    # Handle NULLs and quoted strings properly
    fields = []
    field = ''
    in_str = False
    escape = False

    for char in row_str:
        if in_str:
            if escape:
                field += char
                escape = False
            elif char == '\\':
                field += char
                escape = True
            elif char == "'":
                in_str = False
                fields.append(field)
                field = ''
            else:
                field += char
        else:
            if char == "'":
                in_str = True
            elif char == ',':
                if field.strip().upper() == "NULL":
                    fields.append(None)
                elif field.strip() != '':
                    try:
                        val = int(field)
                        fields.append(val)
                    except ValueError:
                        try:
                            val = float(field)
                            fields.append(val)
                        except ValueError:
                            fields.append(field.strip())
                field = ''
            else:
                field += char

    if field.strip():
        if field.strip().upper() == "NULL":
            fields.append(None)
        else:
            try:
                fields.append(int(field))
            except:
                try:
                    fields.append(float(field))
                except:
                    fields.append(field.strip())

    return fields


class Command(BaseCommand):
    help = 'Import KLFieldtestMeasurements from CSV'

    def create_csv_from_original_dump(self):
        sql_file = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/fieldtest_measurements.sql")
        csv_file = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/data.csv")

        # Read SQL file and extract data
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_data = f.read()

        # Find all insert blocks
        matches = insert_pattern.findall(sql_data)

        # Extract individual rows
        rows = []
        for match in matches:
            for row_match in row_pattern.finditer(match):
                row_str = row_match.group(1)
                parsed = parse_row(row_str)
                if len(parsed) >= 14:
                    rows.append(parsed[:14])

        # Write to CSV
        with open(csv_file, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in rows:
                writer.writerow(row)

        logger.info(" Extracted %s rows to %s.", len(rows), csv_file)
        return csv_file


    def convert_sql_dump_to_csv(self):
        """
        Extracts the COPY data block from an SQL dump and writes it to a CSV file.
        Assumes the COPY block is in PostgreSQL's tab-delimited format.
        """
        sql_dump_path = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/lautrer_wissen_klfieldtestmeasurements.sql")
        output_csv_path = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/lautrer_wissen_klfieldtestmeasurements.csv")
        in_copy_block = False
        headers = [
            "id", "time", "latitude", "longitude", "sats", "battery", "triggered",
            "rssi", "snr", "uplink", "downlink", "created_at", "invalid",
            "payloadHex", "rawdata", "deveui", "city_district_name",
            "data_acquisition_date", "data_source", "insert_timestamp"
        ]

        with open(sql_dump_path, 'r', encoding='utf-8') as infile, \
            open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:

            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()

            for line in infile:
                if line.strip().startswith("COPY") and "lautrer_wissen_klfieldtestmeasurements" in line:
                    in_copy_block = True
                    continue

                if in_copy_block:
                    if line.strip() == r"\.":
                        break  # End of COPY block

                    values = line.rstrip('\n').split('\t')
                    # Handle NULLs (PostgreSQL uses "\N")
                    row = {
                        key: (None if val == r"\N" else val)
                        for key, val in zip(headers, values)
                    }
                    writer.writerow(row)

        logger.info("[✓] Converted SQL COPY to CSV: %s", output_csv_path)
        return output_csv_path 
        

    def handle(self, *args, **kwargs):
        file_path = self.convert_sql_dump_to_csv()
        self.import_measurement_from_csv_file(file_path)

        file_path = self.create_csv_from_original_dump()
        self.import_measurement_from_csv_file(file_path)
    
    def import_measurement_from_csv_file(self, file_path):
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                timestamp = int(row['time'])  # Assuming it’s a Unix timestamp in milliseconds
                dt = datetime.fromtimestamp(timestamp / 1000.0)

                data = dict(
                    time=timestamp,
                    latitude=float(row['latitude']) if row['latitude'] else None,
                    longitude=float(row['longitude']) if row['longitude'] else None,
                    sats=int(row['sats']) if row['sats'] else None,
                    battery=int(row['battery']) if row['battery'] else None,
                    triggered=row['triggered'],
                    rssi=float(row['rssi']) if row['rssi'] else None,
                    snr=float(row['snr']) if row['snr'] else None,
                    uplink=int(row['uplink']) if row['uplink'] else None,
                    downlink=int(row['downlink']) if row['downlink'] else None,
                    invalid=int(row['invalid']) if row['invalid'] else None,
                    payloadHex=row['payloadHex'],
                    rawdata=row['rawdata'],
                    created_at=dt
                )
                self.safe_create_measurement(data)

        logger.info('Successfully imported data.')
    
    def safe_create_measurement(self, data):
        """
        Create a KLFieldtestMeasurements object only if an identical one doesn't already exist.
        `data` should be a dict with keys matching model field names.
        """

        # Build a Q object that checks all fields for equality
        filter_q = Q()
        for field, value in data.items():
            if value is None:
                filter_q &= Q(**{f"{field}__isnull": True})
            else:
                filter_q &= Q(**{field: value})

        # Check if such an object already exists
        if not KLFieldtestMeasurements.objects.filter(filter_q).exists():
            KLFieldtestMeasurements.objects.create(**data)
        else:
            logger.warning("Duplicate entry found for data: %s. Skipping creation.", data)
