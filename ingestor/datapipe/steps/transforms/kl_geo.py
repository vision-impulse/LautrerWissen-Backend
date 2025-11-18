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
import json
import logging
import pandas as pd

from ingestor.datapipe.steps.base_step import DefaultTransformStep
from ingestor.utils.geo_districts import CityDistrictsDecoder
from shapely.geometry import shape, mapping, Polygon, MultiPolygon

logger = logging.getLogger(__name__)


class KLGeoResourceTransformStep(DefaultTransformStep):

    def __init__(self):
        super(KLGeoResourceTransformStep, self).__init__()
        self.model_handlers = {
            "KLParkingLocation": KLGeoResourceTransformStep._transform_parking_location,
            "KLParkingZone": KLGeoResourceTransformStep._transform_parking_zone,
            "KLCityDistrict": KLGeoResourceTransformStep._transform_city_district
        }

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        transform_func = self.model_handlers.get(db_model.__name__, None)
        if transform_func is None:
            logger.info("Unsupported model: %s", db_model)
            return []

        result = []
        with open(download_file) as f:
            geojson_data = json.load(f)
            features = geojson_data['features']
            for feature in features:
                transformed_data = transform_func(feature)
                if transformed_data:
                    transformed_data["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(transformed_data["geometry"])
                    transformed_data["data_source"] = context.resource.data_source
                    transformed_data["data_acquisition_date"] = data_acquisition_date
                    result.append(transformed_data)

        return result

    @staticmethod
    def _transform_parking_location(feature):
        properties = feature['properties']
        if properties["type"] == "city":  # Skip unwanted data
            return None
        return {
            "geometry": shape(feature["geometry"]),
            "name": properties['name'],
            "address": properties['address'],
            "location_type": properties['type'],
            "total_spots": properties['total'],
        }

    @staticmethod
    def _transform_parking_zone(feature):
        properties = feature['properties']
        return {
            "zone": properties['ZONE'],
            "geometry": KLGeoResourceTransformStep._convert_geometry(feature['geometry'])
        }

    @staticmethod
    def _transform_city_district(feature):
        properties = feature['properties']
        return {
            "name": properties['Name'],
            "geometry": KLGeoResourceTransformStep._convert_geometry(feature['geometry'])
        }

    @staticmethod
    def _convert_geometry(geometry):
        """Extracts and converts geometry to a Django-compatible format."""
        coordinates_2d = [
            [[x[0], x[1]] for x in ring] for ring in geometry["coordinates"]
        ]
        polygon_2d = Polygon(coordinates_2d[0])  # Assuming a single ring
        return polygon_2d



