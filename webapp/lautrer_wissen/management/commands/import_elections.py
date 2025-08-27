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
import pandas as pd
import os
import logging

from django.core.management.base import BaseCommand
from lautrer_wissen.models.elections.election_results import ElectionResult, Election
from datetime import datetime
from datetime import date
from settings_seedfiles import SEED_FILES

logger = logging.getLogger("webapp")


CITY_FILTER = "Kreisfreie Stadt Kaiserslautern"
PARTIES = [
    "SPD",
    "CDU",
    "GRÜNE",
    "FDP",
    "AfD",
    "FREIE WÄHLER",
    "Die Linke",
    "Tierschutzpartei",
    "Die PARTEI",
    "Volt",
    "ÖDP",
    "MLPD",
    "BÜNDNIS DEUTSCHLAND",
    "BSW",
]


class CSVElectionResultRow:

    def __init__(self, df):
        self.df = df

    def _map_to_party(self, df):
        mapped_dict = {}
        for old_key, value in df.items():
            if old_key.startswith("D") or old_key.startswith("F"):
                try:
                    # Extract the number from the key (e.g., 'D1' -> 1)
                    # We subtract 1 because list indices are 0-based.
                    # D1 corresponds to mapping_list[0], D2 to mapping_list[1], etc.
                    index_from_key = int(old_key[1:]) - 1
                    if 0 <= index_from_key < len(PARTIES):
                        new_key = PARTIES[index_from_key]
                        mapped_dict[new_key] = value
                    else:
                        # If the index is out of bounds for mapping_list
                        logger.warning(
                            "Warning: Key %s has an index %s out of bounds for mapping_list.",
                            old_key,
                            index_from_key,
                        )
                        mapped_dict[old_key] = (
                            value  # Keep original key if not found in mapping
                        )
                except ValueError:
                    # If the part after 'D' is not a number
                    mapped_dict[old_key] = value  # Keep original key
            else:
                # If the key does not start with 'D', keep it as is
                mapped_dict[old_key] = value
        return mapped_dict

    def get_direct_votes(self):
        df = self.df.filter(regex="^D[0-9]+$")
        df = df.iloc[0].to_dict()
        return self._map_to_party(df)

    def get_secondary_votes(self):
        df = self.df.filter(regex="^F[0-9]+$")
        df = df.iloc[0].to_dict()
        return self._map_to_party(df)

    def get_stats_direct_votes(self):
        columns = {
            "Wahlberechtigte gesamt (A)": "Wahlberechtigte gesamt",
            "Waehler gesamt (B)": "Waehler gesamt",
            "Direktstimmen ungueltige (C)": "Ungueltige Stimmen",
            "Direktstimmen gueltige (D)": "Gueltige Stimmen",
        }
        selected_df = self.df[list(columns.keys())].rename(columns=columns)
        return selected_df.to_dict(orient="records")[0]

    def get_stats_secondary_votes(self):
        columns = {
            "Wahlberechtigte gesamt (A)": "Wahlberechtigte gesamt",
            "Waehler gesamt (B)": "Waehler gesamt",
            "Listenstimmen ungueltige (E)": "Ungueltige Stimmen",
            "Listenstimmen gueltige (F)": "Gueltige Stimmen",
        }
        selected_df = self.df[list(columns.keys())].rename(columns=columns)
        return selected_df.to_dict(orient="records")[0]

    def get_result_table(self):
        direct_votes = self.get_direct_votes()
        direct_stats = self.get_stats_direct_votes()
        secondary_votes = self.get_secondary_votes()
        secondary_stats = self.get_stats_secondary_votes()

        all_unique_keys = PARTIES
        df_data = []
        for key in all_unique_keys:
            row = {
                "Name": key,
                "Direktstimme": direct_votes.get(key, None),
                "Zweitstimme": secondary_votes.get(key, None),
            }
            df_data.append(row)

        all_unique_keys = direct_stats.keys()
        for key in all_unique_keys:
            row = {
                "Name": key,
                "Direktstimme": direct_stats.get(key, None),
                "Zweitstimme": secondary_stats.get(key, None),
            }
            df_data.append(row)
        return df_data


class Command(BaseCommand):
    help = "Import election results from a CSV file into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force reimport even if existing data is present",
        )

    def handle(self, *args, **options):
        force = options["force"]

        if not force and Election.objects.exists():
            logger.warning(
                "Election data already exist. Import will be skipped. "
                "Use python3 manage.py import_elections --force to overwrite."
            )
            return

        if force:
            logger.info("Deleting existing election data.")
            ElectionResult.objects.all().delete()
            Election.objects.all().delete()
        self._import_election()

    def _import_election(self):
        csv_file = SEED_FILES["election_data_file"]

        election = Election.objects.create(
            name="Bundestagswahl 2025",
            date=date(2024, 11, 5),
            data_source="Manual Import",
            data_acquisition_date=date(2024, 11, 5),
            insert_timestamp=datetime.now(),
        )

        df = pd.read_csv(csv_file, sep=";", encoding="utf-8", dtype=str)
        df = df[df["Gemeindename"] == CITY_FILTER]

        self._import_restult_for_district_type(
            df, district_type="GEMEINDE", election=election
        )
        self._import_restult_for_district_type(
            df, district_type="STADTTEIL", election=election
        )
        self._import_restult_for_district_type(
            df, district_type="BRIEFWAHLBEZIRK", election=election
        )
        logger.info(f"Election data successfully imported.")

    def _import_restult_for_district_type(self, df, district_type, election):
        df_stadtteile = df[df["Gebietsart"] == district_type]
        for index, row in df_stadtteile.iterrows():
            row = pd.DataFrame([row], index=[index])
            result_row = CSVElectionResultRow(row)

            ElectionResult.objects.create(
                election=election,
                district_type=district_type,
                district_name=row.iloc[0]["Gebietsname"],
                result_data=json.dumps(
                    {
                        "direct_votes": result_row.get_direct_votes(),
                        "secondary_votes": result_row.get_secondary_votes(),
                        "result_table": result_row.get_result_table(),
                    }
                ),
            )
