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
from django.core.management.base import BaseCommand
from lautrer_wissen.models.geo.kl import KLSensorGrafanaDashboard
import pandas as pd


from datetime import datetime
from datetime import date

from django.contrib.gis.geos import Point


class Command(BaseCommand):
    help = "Import a JSON layer config into the database"

    def handle(self, *args, **kwargs):
        KLSensorGrafanaDashboard.objects.all().delete()

        KLSensorGrafanaDashboard.objects.create(
            name="HSG-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/public-dashboards/5cc28ae1bfab42dda2d495d11485fb26",
            geometry=Point(7.7498212,49.4387123),
            size_radius_meters=10,
            timefilters="täglich")

        KLSensorGrafanaDashboard.objects.create(
            name="HSG-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/hsg_1w",
            geometry=Point(7.7498212,49.4387123),
            size_radius_meters=10,
            timefilters="wöchentlich")

        KLSensorGrafanaDashboard.objects.create(
            name="HSG-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/hsg_1m",
            geometry=Point(7.7498212,49.4387123),
            size_radius_meters=10,
            timefilters="monatlich")

        KLSensorGrafanaDashboard.objects.create(
            name="Eselsbach-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/pegel_eselsbach",
            geometry=Point(7.761743,49.459719),
            size_radius_meters=10,
            timefilters="Pegelstand")
        
        KLSensorGrafanaDashboard.objects.create(
            name="Waschmühle-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/wesch",
            geometry=Point(7.762565,49.460629),
            size_radius_meters=10,
            timefilters="Temperatur Schwimmbecken")

        KLSensorGrafanaDashboard.objects.create(
            name="Baumgesundheit-Dashboard",
            dashboard_url="https://dash.kaiserslautern.digital/bauag",
            geometry=Point(7.787932,49.451428),
            size_radius_meters=10,
            timefilters="Bodenfeuchte")
        self.stdout.write(self.style.SUCCESS("KLSensorGrafanaDashboard imported successfully."))
