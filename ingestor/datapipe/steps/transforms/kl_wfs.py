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
from ingestor.utils.geo_districts import CityDistrictsDecoder

import json
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from datetime import datetime, date


def parse_date(construction_str: str) -> date | None:
    try:
        if not construction_str:
            raise ValueError("Empty string provided")
        return datetime.strptime(construction_str, "%Y-%m-%d").date()
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None


class KLWFSTransformStep(DefaultTransformStep):
    """WFS-specific transform step."""

    EDUCATIONAL_INSTITUTION_MAP = {
        "gml_id": "gml_id",
        "gid": "gid",
        "bildungs": "education_type",
        "bildung0": "education_subtype",
        "name": "name",
        "erw_name": "extended_name",
        "adresse": "address",
        "plz": "postal_code",
        "ort": "city",
        "internet": "website_url",
    }

    SCULPTURE_MAP = {
        "gml_id": "gml_id",
        "gid": "gid",
        "foto": "photo_url",
        "name": "name",
        "kuenstler": "artist",
        "entstehung": "year_created",
        "quelle": "source",
        "kategorie": "category",
        "standort": "location_name",
    }

    def __init__(self):
        super(KLWFSTransformStep, self).__init__()
        self.model_handlers = {
            "kl_wfs_building_area_sites.geojson": KLWFSTransformStep._transform_vacant_lot,
            "kl_wfs_construction_sites_ongoing.geojson": KLWFSTransformStep._transform_construction_site,
            "kl_wfs_building_right_sites.geojson": KLWFSTransformStep._transform_land_use_plan,
            "kl_wfs_education_sites.geojson": KLWFSTransformStep._transform_educational_institution,
            "kl_wfs_sculptures.geojson": KLWFSTransformStep._transform_sculpture,
        }

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        transform_func = self.model_handlers.get(context.resource.filename)
        if not transform_func:
            raise ValueError(f"Unsupported model: {db_model}")

        result = []
        with open(download_file) as f:
            geojson_data = json.load(f)
            features = geojson_data['features']
            for feature in features:
                transformed_data = transform_func(feature, db_model)
                if transformed_data:
                    transformed_data["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(transformed_data["geometry"])
                    transformed_data["data_source"] = context.resource.data_source
                    transformed_data["data_acquisition_date"] = data_acquisition_date
                    result.append(transformed_data)
        return result

    @staticmethod
    def _transform_vacant_lot(feature, db_model):
        properties = feature['properties']
        geom_shape = KLWFSTransformStep._convert_geometry(feature['geometry'])

        fields = KLWFSTransformStep._extract_fields(properties, db_model)

        fields['geometry'] = geom_shape
        return fields

    @staticmethod
    def _transform_construction_site(feature, db_model):
        properties = feature['properties']
        fields = KLWFSTransformStep._extract_fields(properties, db_model)
        fields['geometry'] = shape(feature["geometry"])
        fields['baustart'] = parse_date(fields["baustart"])
        fields['bauende'] = parse_date(fields["bauende"])
        return fields


    @staticmethod
    def _transform_land_use_plan(feature, db_model):
        properties = feature['properties']
        fields = KLWFSTransformStep._extract_fields(properties, db_model)
        fields['geometry'] = shape(feature["geometry"])
        fields["kl_id"] = fields.pop('id', None)  # Rename 'id' to 'kl_id' safely
        return fields


    @staticmethod
    def _transform_sculpture(feature, db_model):
        properties = feature['properties']
        properties = KLWFSTransformStep.map_properties(properties, KLWFSTransformStep.SCULPTURE_MAP)
        fields = KLWFSTransformStep._extract_fields(properties, db_model)
        fields['geometry'] = shape(feature["geometry"])
        return fields

    @staticmethod
    def _transform_educational_institution(feature, db_model):
        properties = feature['properties']
        properties = KLWFSTransformStep.map_properties(properties, KLWFSTransformStep.EDUCATIONAL_INSTITUTION_MAP)
        fields = KLWFSTransformStep._extract_fields(properties, db_model)
        fields['geometry'] = shape(feature["geometry"])
        return fields

    @staticmethod
    def map_properties(properties, mapping):
        """Maps JSON properties to database fields based on a given mapping dictionary."""
        return {db_field: properties.get(json_key) for json_key, db_field in mapping.items()}

    @staticmethod
    def _extract_fields(properties, db_model):
        row = properties
        fields = {
            field.name: row.get(field.name)
            for field in db_model._meta.fields
            if field.name in row
        }
        return fields

    @staticmethod
    def _convert_geometry(geometry):
        """Extracts and converts geometry to a Django-compatible format."""
        coordinates_2d = [
            [[x[0], x[1]] for x in ring] for ring in geometry["coordinates"]
        ]
        polygon_2d = Polygon(coordinates_2d[0])  # Assuming a single ring
        return polygon_2d
