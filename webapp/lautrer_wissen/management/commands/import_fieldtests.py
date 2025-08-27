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
import logging
import os

from django.core.management.base import BaseCommand
from django.db.models import Q
from datetime import datetime
from lautrer_wissen.models.geo.kl import KLFieldtestMeasurements
from settings_seedfiles import SEED_FILES

logger = logging.getLogger("webapp")

columns = [
    "time", "payloadHex", "battery", "latitude", "longitude", "sats",
    "triggered", "rssi", "snr", "uplink", "downlink", "deveui", "invalid", "rawdata"
]

# Regex pattern to extract values from the INSERT statement
insert_pattern = re.compile(r"INSERT INTO.*?VALUES\s*(.+);", re.DOTALL)
row_pattern = re.compile(r"\((.*?)\),?", re.DOTALL)

def parse_row(row_str):
    """Parses a single SQL value row into Python data types."""
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
    help = 'Import fieldtest measurements from a SQL-Dump (db dump by Herzlich Digital).'

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and KLFieldtestMeasurements.objects.exists():
            logger.warning(
                "Fieldtest data already exist. Import will be skipped. "
                "Use python3 manage.py import_fieldtests --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing fieldtest data.")
            KLFieldtestMeasurements.objects.all().delete()
        self._import_fieldtest_data()


    def _import_fieldtest_data(self):
        sql_file_path = SEED_FILES["fieldtest_sql_file"]
        csv_file_path = "./fieldtest_tmp.csv"
        try:
            self._create_csv_from_original_sql_dump(sql_file_path, csv_file_path)
            self._import_measurement_from_csv_file(csv_file_path)
            os.remove(csv_file_path)
        except Exception as ex:
            logger.error("Error importing fieldtest data (%s)", ex)

    def _create_csv_from_original_sql_dump(self, sql_file, csv_file):
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
    
    def _import_measurement_from_csv_file(self, csv_file_path):
        
        with open(csv_file_path, newline='') as csvfile:
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
                self._safe_create_measurement(data)

        logger.info('Successfully imported fieldtest data.')
    
    def _safe_create_measurement(self, data):
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
