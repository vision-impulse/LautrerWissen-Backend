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
from django.core.management.base import BaseCommand
from lautrer_wissen.models import DemographicData
import os 

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
    "18": "Erfenbach"
}

class Command(BaseCommand):
    help = "Import demographic data from a CSV file"

    def handle(self, *args, **options):
        csv_file = os.path.join(os.getenv("APP_DATA_DIR"), "initial/data/demographics.csv")

        DemographicData.objects.all().delete()
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}.'))
            return 

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            count = 0
            for row in reader:
                stichtag_str = str(row['stichtag'])
                stichtag_date = datetime.datetime.strptime(stichtag_str, "%Y%m%d").date()

                DemographicData.objects.update_or_create(
                    city_district_id=int(row['ortsbezirk_id']),
                    city_district_name=MAPPING.get(str(int(row['ortsbezirk_id'])), "None"),
                    age_group=row['altersgruppe_destatis'],
                    gender=row['geschlecht'],
                    reporting_date=stichtag_date,
                    defaults={
                        'number': int(row['anzahl'])
                    }
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'Imported {count} records successfully.'))

