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

from ingestor.datapipe.steps.base_step import DefaultTransformStep

import os
import importlib

from datetime import datetime

import json
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
import yaml
import os
from ingestor.utils.geo_districts import CityDistrictsDecoder
from shapely.geometry import Point


class KLSensorsTransformStep(DefaultTransformStep):
    """OSM-specific transform step."""

    SENSOR_TYPES = [
        ('weather', 'Wetterstation'),
        ('particle', 'Luftqualität'),
        ('sound', 'Geräuschpegel'),
        ('distance', 'Abstandssensor'),
        ('distance_lidar', 'Abstandssensor'),
        ('distance_ultrasonic', 'Abstandssensor'),
        ('temperature', 'Temperatur'),
        ('moisture', 'Feuchtigkeit'),
        ('particle_temp', 'Luftqualität & Temperatur'),
        ('temperature_multi', 'Temperatur'),
    ]

    def __init__(self):
        super(KLSensorsTransformStep, self).__init__()
        self.sensor_type_map = dict(KLSensorsTransformStep.SENSOR_TYPES)

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        result = []
        with open(download_file, 'r') as file:
            mqtt_resources = yaml.safe_load(file)
            for mqtt_res in mqtt_resources["sensors"]:
                print("Loading KLEnvironmentalSensor: ", mqtt_res["topic"])

                sensor_type = "Unbekannt"
                for (k, v) in KLSensorsTransformStep.SENSOR_TYPES:                
                    if k in mqtt_res["topic"]:
                        sensor_type = v
                        break

                position = Point(mqtt_res["sensor_longitude"], mqtt_res["sensor_latitude"])
                row = dict(sensor_topic=mqtt_res["topic"],
                           sensor_type=sensor_type,
                           geometry=position,
                           city_district_name=CityDistrictsDecoder.get_district_name_for_geometry(position),
                           data_source=context.resource.data_source,
                           data_acquisition_date=data_acquisition_date)
                result.append(row)
        return result
