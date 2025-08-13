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

from ingestor.datapipe.steps.base_step import PipelineStep
from ingestor.utils.geo_districts import CityDistrictsDecoder
import geopandas as gpd

import logging

logger = logging.getLogger(__name__)


class FilterStep(PipelineStep):

    def __init__(self):
        super(FilterStep, self).__init__(next_step=None)

    def execute(self, context):
        logger.info("Filter objects by geographic region ...")
        try:
            rows = context.get_data("rows")

            gdf = gpd.GeoDataFrame(rows, geometry='geometry')
            gdf = CityDistrictsDecoder.filter_points_by_city_polygon(gdf, buffer_km=4)
            rows = gdf.to_dict(orient='records')

            context.set_data("rows", rows)
            return True
        except Exception as e:
            logger.error("Filter failed for %s", context.resource, exc_info=True)
            return False



