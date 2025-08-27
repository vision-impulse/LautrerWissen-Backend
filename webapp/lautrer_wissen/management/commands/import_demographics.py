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
import datetime
import os
import logging

from django.core.management.base import BaseCommand
from lautrer_wissen.models import DemographicData
from settings_seedfiles import SEED_FILES
from collections import defaultdict

logger = logging.getLogger("webapp")

MAPPING = {
    "1": "Innenstadt-Ost",
    "2": "Innenstadt-Südwest",
    "3": "Innenstadt West/Kotten",
    "4": "Innenstadt Nord/Kaiserberg",
    "5": "Grübentälchen/Volkspark",
    "6": "Betzenberg",
    "7": "Lämmchesberg/Uniwohnstadt",
    "8": "Bännjerrück/Karl-Pfaff-S.",
    "9": "Kaiserslautern-West",
    "10": "Erzhütten/Wiesenthalerhof",
    "11": "Einsiedlerhof",
    "12": "Morlautern",
    "13": "Erlenbach",
    "14": "Mölschbach",
    "15": "Dansenberg",
    "16": "Hohenecken",
    "17": "Siegelbach",
    "18": "Erfenbach",
}


class Command(BaseCommand):
    help = "Import demographic data from a CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and DemographicData.objects.exists():
            logger.warning(
                "Demographic data already exist. Import will be skipped. "
                "Use python3 manage.py import_demographics --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing demographic data.")
            DemographicData.objects.all().delete()
        self._import_demographic_data()

    def _import_demographic_data(self):
        csv_file = SEED_FILES["demographics_data_file"]
        if not os.path.exists(csv_file):
            logger.error("File for data import not found: %s." % (csv_file))
            return

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            aggregated = defaultdict(int)

            for row in reader:
                reporting_date_str = str(row["stichtag"])
                reporting_date = datetime.datetime.strptime(
                    reporting_date_str, "%Y%m%d"
                ).date()

                DemographicData.objects.update_or_create(
                    city_district_id=int(row["ortsbezirk_id"]),
                    city_district_name=MAPPING.get(
                        str(int(row["ortsbezirk_id"])), "None"
                    ),
                    age_group=row["altersgruppe_destatis"],
                    gender=row["geschlecht"],
                    reporting_date=reporting_date,
                    defaults={"number": int(row["anzahl"])},
                )

                # --- aggregated totals across all districts ---
                key = (row["altersgruppe_destatis"], row["geschlecht"], reporting_date)
                aggregated[key] += int(row["anzahl"])

            for (age_group, gender, reporting_date), total in aggregated.items():
                DemographicData.objects.update_or_create(
                    city_district_id=0,
                    city_district_name="Gesamt Kaiserslautern",
                    age_group=age_group,
                    gender=gender,
                    reporting_date=reporting_date,
                    defaults={"number": total},
                )

            logger.info("Demographic data successfully imported.")
