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

import json
import pandas as pd
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import datetime
from ingestor.utils.geo import remove_z_dimension
from ingestor.utils.geo_districts import CityDistrictsDecoder

import geopandas as gpd
import os

class WifiTransformStep(DefaultTransformStep):

    def transform(self, context, db_model, data_acquisition_date):
        if "freifunk" in context.resource.filename: # check
            return WifiTransformStep._read_freifunk_json_as_df(context, db_model, data_acquisition_date)
        elif "empera" in context.resource.filename:
            return WifiTransformStep._read_empera_kml_as_df(context, db_model)
        return WifiTransformStep._read_myspot_excell_as_df(context, db_model)

    @staticmethod
    def _read_freifunk_json_as_df(context, db_model, data_acquisition_date):
        download_file = os.path.join(context.out_dir, context.resource.filename)
        with open(download_file, "r") as file:
            data = json.load(file)
            df = pd.DataFrame(data["nodes"])
            df = df.dropna(subset=['location', 'hostname'])
            df["geometry"] = df["location"].apply(lambda loc: Point(loc["longitude"], loc["latitude"]))
            rows_as_dict = df[["hostname", "geometry"]].rename(columns={"hostname": "name"}).to_dict(orient="records")

            result = []
            for row in rows_as_dict:
                fields = {
                    field.name: row.get(field.name)
                    for field in db_model._meta.fields
                    if field.name in row
                }
                fields["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(fields["geometry"])
                fields["data_source"] = context.resource.data_source
                fields["data_acquisition_date"] = data_acquisition_date
                result.append(fields)
            return result

    @staticmethod
    def _read_myspot_excell_as_df(context, db_model):
        json_filepath = os.path.join(context.out_dir, context.resource.filename)
        df = pd.read_excel(json_filepath)
        df = df.rename(columns={"Standortname": "Name"})
        df["geometry"] = df.apply(lambda row: Point(row["Longitude"], row["Latitude"]), axis=1)
        df = df[["Name", "geometry"]]
        rows_as_dict = df.to_dict(orient="records")

        result = []
        for row in rows_as_dict:
            fields = {
                field.name: row.get(field.name)
                for field in db_model._meta.fields
                if field.name in row
            }
            fields["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(fields["geometry"])
            fields["data_source"] = context.resource.data_source
            fields["data_acquisition_date"] = datetime.now().date() # check
            result.append(fields)
        return result

    @staticmethod
    def _read_empera_kml_as_df(context, db_model):
        json_filepath = os.path.join(context.out_dir, context.resource.filename)
        gdf = gpd.read_file(json_filepath, driver="LIBKML")
        gdf["geometry"] = gdf.geometry.apply(remove_z_dimension)
        gdf = gdf.rename(columns={"Name": "name", "Description": "description"}, errors="raise")
        rows_as_dict = gdf.to_dict(orient='records')

        result = []
        for row in rows_as_dict:
            fields = {
                field.name: row.get(field.name)
                for field in db_model._meta.fields
                if field.name in row
            }
            fields["city_district_name"] = CityDistrictsDecoder.get_district_name_for_geometry(fields["geometry"])
            fields["data_source"] = context.resource.data_source
            fields["data_acquisition_date"] = datetime.strptime('15012025', '%d%m%Y').date() # check
            result.append(fields)
        return result
