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
import logging

logger = logging.getLogger(__name__)


def parse_date(construction_str: str) -> date | None:
    try:
        if not construction_str:
            raise ValueError("Empty string provided")
        return datetime.strptime(construction_str, "%Y-%m-%d").date()
    except ValueError as e:
        logger.error("Error parsing date: %s", construction_str, exc_info=True)
        return None


class WFSTransformStep(DefaultTransformStep):
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
        super(WFSTransformStep, self).__init__()
        self.model_handlers = {
            "KLVacantLot": WFSTransformStep._transform_vacant_lot,
            "KLConstructionSite": WFSTransformStep._transform_construction_site,
            "KLLandUsePlan": WFSTransformStep._transform_land_use_plan,
            "KLEducationalInstitution": WFSTransformStep._transform_educational_institution,
            "KLSculpture": WFSTransformStep._transform_sculpture,
        }

    def transform(self, context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)

        with open(download_file) as f:
            geojson_data = json.load(f)
            features = geojson_data['features']
        
        return self.apply_transform_function(features, db_model, data_acquisition_date, context)

    def apply_transform_function(self, features, db_model, data_acquisition_date, context):
        result = []
        transform_func = self.model_handlers.get(db_model.__name__, None)
        if transform_func is None:
            logger.info("Unsupported model: %s", db_model)

        for feature in features:
            transformed_data = {}
            if transform_func is not None:
                transformed_data = transform_func(feature, db_model)

            geometry = WFSTransformStep._convert_geometry(feature['geometry'])    
            transformed_data["geometry"] = geometry
            transformed_data["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(geometry)
            transformed_data["data_source"] = context.resource.data_source
            transformed_data["data_acquisition_date"] = data_acquisition_date
            result.append(transformed_data)
        return result

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
        """
        Extracts and converts geometry to a Django-compatible format.
        If geometry is a Polygon, convert to 2D polygon (drop Z if present).
        Otherwise, fall back to shapely.shape().
        """
        geom_type = geometry.get("type")

        if geom_type == "Polygon":
            # Drop Z dimension if present
            coordinates_2d = [
                [[coord[0], coord[1]] for coord in ring]
                for ring in geometry.get("coordinates", [])
            ]
            # Assuming a single ring (outer boundary)
            return Polygon(coordinates_2d[0])

        # Fallback for other geometry types
        return shape(geometry)

    # ------------------------------------------------------------------------------------------
    # Specific handlers for model transformation

    @staticmethod
    def _transform_vacant_lot(feature, db_model):
        fields = WFSTransformStep._extract_fields(feature['properties'], db_model)
        return fields

    @staticmethod
    def _transform_construction_site(feature, db_model):
        fields = WFSTransformStep._extract_fields(feature['properties'], db_model)
        fields['baustart'] = parse_date(fields["baustart"])
        fields['bauende'] = parse_date(fields["bauende"])
        return fields

    @staticmethod
    def _transform_land_use_plan(feature, db_model):
        fields = WFSTransformStep._extract_fields(feature['properties'], db_model)
        fields["kl_id"] = fields.pop('id', None)  # Rename 'id' to 'kl_id' safely
        return fields

    @staticmethod
    def _transform_sculpture(feature, db_model):
        properties = WFSTransformStep.map_properties(feature['properties'], WFSTransformStep.SCULPTURE_MAP)
        fields = WFSTransformStep._extract_fields(properties, db_model)
        return fields

    @staticmethod
    def _transform_educational_institution(feature, db_model):
        properties = WFSTransformStep.map_properties(feature['properties'], WFSTransformStep.EDUCATIONAL_INSTITUTION_MAP)
        fields = WFSTransformStep._extract_fields(properties, db_model)
        return fields
